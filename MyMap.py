import numpy as np
from queue import Queue
import random

Direction = {
	"RIGHT":0, "UP":1, "LEFT":2, "DOWN":3, "NONE":-1
}

MoveTO = []

MoveTO.append(np.array([0, -1]))	# UP
MoveTO.append(np.array([-1, 0]))  # LEFT
MoveTO.append(np.array([1, 0]))		# RIGHT
MoveTO.append(np.array([0, 1]))		# DOWN

MoveTO.append(np.array([1, -1]))	
MoveTO.append(np.array([1, 1]))
MoveTO.append(np.array([-1, 1]))	
MoveTO.append(np.array([-1, -1]))	

	


# 输入：一条线段的两个端点
# 输出：整点集合
def Init_Exit(P1, P2):
	exit = list()
	
	if P1[0]==P2[0]:
		x = P1[0]
		for y in range(P1[1], P2[1]+1):
			exit.append((x, y))
	elif P1[1]==P2[1]:
		y = P1[1]
		for x in range(P1[0], P2[0]+1):
			exit.append((x, y))
	# 斜线 
	else :
		pass

	return exit

# Fire


def Init_Fire(P1, P2):
	fire = list()

	if P1[0] == P2[0]:
		x = P1[0]
		for y in range(P1[1], P2[1]+1):
			fire.append((x, y))
	elif P1[1] == P2[1]:
		y = P1[1]
		for x in range(P1[0], P2[0]+1):
			fire.append((x, y))
	# 斜线
	else:
		pass

	return fire

# 两点坐标围成的矩形区域
def Init_Barrier(A, B):
	if A[0]>B[0]:
		A, B = B, A

	x1, y1 = A[0], A[1]
	x2, y2 = B[0], B[1]

	if y1<y2:
		return ((x1, y1), (x2, y2))
	else:
		return ((x1, y2), (x2, y1))


# 
# 外墙宽度 
# Size
Outer_Size = 2

# 障碍 	-1
# LEFT 	0
# UP	1
# RIGHT 2
# DOWN  3


class Map:
	def __init__(self, L, W, E, B, F):
		self.Length = L
		self.Width = W
		self.Exit = E
		self.Barrier = B
		self.barrier_list = []
		self.CompeteStatus = np.zeros((self.Length+Outer_Size*2, self.Width+Outer_Size*2))
		# 威胁场
		self.Fire = F
		self.FireDegree = np.zeros(((self.Length+Outer_Size*2), (self.Width+Outer_Size*2)))
		# 0~L+1
		# 0~W+1
		# 势能
		# 出口为 1
		# 障碍为 inf
		self.space = np.zeros((self.Length+Outer_Size*2, self.Width+Outer_Size*2))
		for j in range(0, self.Width+Outer_Size*2):
			self.space[0][j] = self.space[L+1][j] = float("inf")
			self.barrier_list.append((0, j))
			self.barrier_list.append((L+1, j))

		for i in range(0, self.Length+Outer_Size*2):
			self.space[i][0] = self.space[i][W+1] = float("inf")
			self.barrier_list.append((i, 0))
			self.barrier_list.append((i, W+1))

		for (A, B) in self.Barrier:
			for i in range(A[0], B[0]+1):
				for j in range(A[1], B[1]+1):
					self.space[i][j] = float("inf")
					self.barrier_list.append((i, j))

		# 出口

		for (ex, ey) in self.Exit:
			# print(str(ex) + " and " + str(ey))
			self.space[ex][ey] = 1
			if ex==self.Length:
				self.space[ex+1][ey] = 1
			if ey==self.Width:
				self.space[ex][ey+1] = 1
			# #print("%d %d"%(ex, ey))
			if (ex, ey) in self.barrier_list:
				self.barrier_list.remove((ex, ey))

		# #print(self.barrier_list)

		# #print(type(self.space))
		# 
		# 显示全部
		# #print(self.space)
		
		self.Init_Potential()
		# self.calFij()
		# self.print(self.space)


	def print(self, mat):
		for line in mat:
			for v in line:
				print(v, end=' ')
			print("")
	
	def Check_Valid(self, x, y):
		# pass
		x, y = int(x), int(y)
		if x>self.Length+1 or x<0 or y>self.Width+1 or y<0:
			return False

		if self.space[x][y]==float("inf"):
			return False
		else:
			return True
			
	def checkSavefy(self, pos):
		x, y = int(pos[0]), int(pos[1])
		if x==self.Length+1:
			x -= 1
		elif x==-1:
			x += 1
		if y==self.Width+1:
			y -= 1
		elif y==-1:
			y -= 0

		if (x, y) in self.Exit:
			return True
		else:
			return False

	def getDeltaP(self, P1, P2):
		x1, y1 = int(P1[0]), int(P1[1])
		x2, y2 = int(P2[0]), int(P2[1])
		deltaP = float(self.space[x1][y1] - self.space[x2][y2])
		if (x1+x2) % 2 != 0 and (y1+y2) % 2 != 0:
			deltaP /= 1.4

		return deltaP

	def calFij(self):
		# 火灾的位置
		minDis = np.zeros((self.Length+Outer_Size*2, self.Width+Outer_Size*2))
		for i in range(self.Length+Outer_Size*2):
			for j in range(self.Width+Outer_Size*2):
				minDis[i][j] = float("inf")

		# #print(minDis)
		#print(sx, sy)
		for (pos_fx, pos_fy) in self.Fire:
			# print(self.Fire)
			tmp = self.BFS(pos_fx, pos_fy)
			# print(tmp)
			# self.#print(tmp)
			#print("----")
			for i in range(self.Length+Outer_Size*2):
				for j in range(self.Width+Outer_Size*2):
					minDis[i][j] = min(minDis[i][j], tmp[i][j]) + 1

		line = 30
		sumFire = 0
		for i in range(self.Length+Outer_Size*2):
			for j in range(self.Width+Outer_Size*2):
				# if(self.FireDegree[i][j] >= 20):
				# 	self.FireDegree[i][j] = 0
				if self.Check_Valid(i, j) and minDis[i][j] <= line:
					sumFire += 1.0 / minDis[i][j]
			
		# print(np.min(self.FireDegree))
		# print(np.max(self.FireDegree))
		for i in range(self.Length+Outer_Size*2):
			for j in range(self.Width+Outer_Size*2):
				if self.Check_Valid(i,j) and minDis[i][j] <= line:
						self.FireDegree[i][j] = 1.0 / minDis[i][j] / sumFire 
				else:
					self.FireDegree[i][j] = 0
		
		self.FireDegree *= 50
		print(np.max(self.FireDegree))
		print(np.sum(self.FireDegree))

	def Init_Potential(self):
		minDis = np.zeros((self.Length+Outer_Size*2, self.Width+Outer_Size*2))
		for i in range(self.Length+Outer_Size*2):
			for j in range(self.Width+Outer_Size*2):
				minDis[i][j] = float("inf")

		# #print(minDis)
		for (sx, sy) in self.Exit:
			#print(sx, sy)
			tmp = self.BFS(sx, sy)
			# self.#print(tmp)
			#print("----")
			for i in range(self.Length+Outer_Size*2):
				for j in range(self.Width+Outer_Size*2):
					minDis[i][j] = min(minDis[i][j], tmp[i][j])

		self.space = minDis
		# return minDis
		# #print(minDis)

	def BFS(self, x, y):
		if not self.Check_Valid(x, y):
			return


		tmpDis = np.zeros((self.Length+Outer_Size*2, self.Width+Outer_Size*2))
		for i in range(self.Length+Outer_Size*2):
			for j in range(self.Width+Outer_Size*2):
				tmpDis[i][j] = self.space[i][j]

		queue = Queue()
		queue.put((x, y))
		tmpDis[x][y] = 1
		while not queue.empty():
			(x, y) = queue.get()
			dis = tmpDis[x][y]
			# if dis>0:
			# 	continue

			for i in range(8):
				move = MoveTO[i]
				(nx, ny) = (x, y) + move
				if self.Check_Valid(nx, ny) and tmpDis[nx][ny]==0:
					queue.put((nx, ny))
					tmpDis[nx][ny] = dis + (1.0 if i<4 else 1.4) # 0 1 2 3 表示上下左右

		return tmpDis

	def Random_Valid_Point_l(self, level):
		l_lo = 1
		l_hi = self.Length

		if level == -2:
			l_lo = 1
			l_hi = 18
		elif level == -1:
			l_lo = 19
			l_hi =  37
		elif level == 0:
			l_lo = 38
			l_hi = 56
		elif level == 1:
			l_lo = 56
			l_hi = 75
		elif level == 2:
			l_lo = 77
			l_hi = 95

		x = random.uniform(l_lo, l_hi+2)
		y = random.uniform(1, self.Width+2)
		while not myMap.Check_Valid(x, y):
			x = random.uniform(l_lo, l_hi+2)
			y = random.uniform(1, self.Width+2)

		return x, y



	def Random_Valid_Point(self):
		x = random.uniform(1, self.Length+2)
		y = random.uniform(1, self.Width+2)
		while not myMap.Check_Valid(x, y):
			x = random.uniform(1, self.Length+2)
			y = random.uniform(1, self.Width+2)

		return x, y

def Init_Map():
	# 房间长宽
	# Length = 190
	# Width = 280

	# 出口 
	# 点集
	Exit = Init_Exit(P1=(60, 2/4), P2=(60, 4))

	Exit.extend(Init_Exit(P1=(0, 8), P2=(0, 9)))

	# 障碍 矩形区域
	Barrier = list()
	# Barrier.append(Init_Barrier(A=(0, 5), B=(30, 7)))
	# Barrier.append(Init_Barrier(A=(10, 6), B=(15, 8)))

	Barrier.append(Init_Barrier(A=(0, 0), B=(30, 196)))
	Barrier.append(Init_Barrier(A=(30, 112), B=(60, 280)))
	Barrier.append(Init_Barrier(A=(60, 168), B=(120, 196)))
	Barrier.append(Init_Barrier(A=(60, 252), B=(120, 280)))
	Barrier.append(Init_Barrier(A=(150, 0), B=(180, 196)))
	# print(Exit)
	return Map(L=Length, W=Width, E=Exit, B=Barrier)


# # 房间长宽
# Length = 30
# Width = 20

# # 出口 
# # 点集
# Exit = Init_Exit(P1=(30, 4), P2=(30, 7))
# Exit.extend(Init_Exit(P1=(30, 15), P2=(30, 18)))

# # 障碍 矩形区域
# Barrier = list()
# Barrier.append(Init_Barrier(A=(3, 5), B=(10, 12)))
# Barrier.append(Init_Barrier(A=(14, 0), B=(16, 15)))
# Barrier.append(Init_Barrier(A=(20, 9), B=(21, 20)))


# myMap = Map(L=Length, W=Width, E=Exit, B=Barrier)

# 房间长宽
Length = 95
Width = 28

# # 出口 
# # 点集
# Exit = Init_Exit(P1=(100, 28), P2=(100, 32))
# Exit.extend(Init_Exit(P1=(0, 28), P2=(0, 32)))

# # 障碍 矩形区域
# Barrier = list()
# Barrier.append(Init_Barrier(A=(24, 0), B=(26, 38)))
# Barrier.append(Init_Barrier(A=(49, 20), B=(51, 60)))
# Barrier.append(Init_Barrier(A=(74, 0), B=(76, 30)))


# myMap =  Map(L=Length, W=Width, E=Exit, B=Barrier)


# 出口 
# 点集

#Exit = list()
# Exit = Init_Exit(P1=(100, 25), P2=(100, 35))
# Exit.extend(Init_Exit(P1=(0, 25), P2=(0, 35)))
# Exit.extend(Init_Exit(P1=(30, 10), P2=(50, 10)))
# Exit.extend(Init_Exit(P1=(0, 25), P2=(0, 35)))

# Exit = Init_Exit(P1=(int(60/4), int(56/4)), P2=(int(120/4), int(56/4)))
Exit = Init_Exit(P1=(5, 12), P2=(5, 15))
Exit.extend(Init_Exit(P1=(7, 18), P2=(10, 18)))
Exit.extend(Init_Exit(P1=(13, 12), P2=(13, 15)))
# 额外

#Exit.extend(Init_Exit(P1=(91, 23), P2=(91, 25)))
Exit.extend(Init_Exit(P1=(52, 23), P2=(52, 25)))


Fire = Init_Fire(P1=(int(40/4), int(230/4)), P2=(int(50/4), int(230/4)))
# 障碍 矩形区域



Barrier = list()

# -2
Barrier.append(Init_Barrier(A=(3, 0), B=(6, 11)))
Barrier.append(Init_Barrier(A=(12, 0), B=(15, 11)))
Barrier.append(Init_Barrier(A=(6, 0), B=(12, 3)))
Barrier.append(Init_Barrier(A=(6, 6), B=(7, 17)))


Barrier.append(Init_Barrier(
	A=(3, 13), B=(4, 14)))
Barrier.append(Init_Barrier(
	A=(3, 16), B=(4, 17)))

Barrier.append(Init_Barrier(
	A=(14,13), B=(15, 14)))
Barrier.append(Init_Barrier(
	A=(14, 16), B=(15, 17)))


Barrier.append(Init_Barrier(A=(3, 0), B=(15, 11)))
Barrier.append(Init_Barrier(A=(6, 11), B=(12, 17)))

Barrier.append(Init_Barrier(A=(10, 6), B=(12, 17)))
Barrier.append(Init_Barrier(A=(0, 20), B=(3, 30)))

Barrier.append(Init_Barrier(A=(6, 20), B=(12, 25)))
Barrier.append(Init_Barrier(A=(15, 20), B=(18,30)))

# -2 to -1
Barrier.append(Init_Barrier(A=(18, 0), B=(19, 6)))
Barrier.append(Init_Barrier(A=(18, 8), B=(19, 29)))
# -1
Barrier.append(Init_Barrier(A=(22, 0), B=(25, 11)))
Barrier.append(Init_Barrier(A=(31, 0), B=(34, 11)))
Barrier.append(Init_Barrier(A=(25, 0), B=(31, 3)))
Barrier.append(Init_Barrier(A=(25, 6), B=(26, 17)))


Barrier.append(Init_Barrier(
	A=(22, 13), B=(23, 14)))
Barrier.append(Init_Barrier(
	A=(22, 16), B=(23, 17)))

Barrier.append(Init_Barrier(
	A=(33, 13), B=(34, 14)))
Barrier.append(Init_Barrier(
	A=(33, 16), B=(34, 17)))


Barrier.append(Init_Barrier(A=(22, 0), B=(34, 11)))
Barrier.append(Init_Barrier(A=(25, 11), B=(31, 17)))

Barrier.append(Init_Barrier(A=(29, 6), B=(31, 17)))
Barrier.append(Init_Barrier(A=(19, 20), B=(22, 30)))

Barrier.append(Init_Barrier(A=(25, 20), B=(31, 25)))
Barrier.append(Init_Barrier(A=(34, 20), B=(37, 30)))

# -1 to 0
Barrier.append(Init_Barrier(A=(37, 0), B=(38, 6)))
Barrier.append(Init_Barrier(A=(37, 8), B=(38, 29)))

# -1
Barrier.append(Init_Barrier(A=(41, 0), B=(44, 11)))
Barrier.append(Init_Barrier(A=(50, 0), B=(34+19, 11)))
Barrier.append(Init_Barrier(A=(25+19, 0), B=(31+19, 3)))
Barrier.append(Init_Barrier(A=(25+19, 6), B=(26+19, 17)))


Barrier.append(Init_Barrier(
	A=(22+19, 13), B=(23+19, 14)))
Barrier.append(Init_Barrier(
	A=(22+19, 16), B=(23+19, 17)))

Barrier.append(Init_Barrier(
	A=(33+19, 13), B=(34+19, 14)))
Barrier.append(Init_Barrier(
	A=(33+19, 16), B=(34+19, 17)))


Barrier.append(Init_Barrier(A=(22+19, 0), B=(34+19, 11)))
Barrier.append(Init_Barrier(A=(25+19, 11), B=(31+19, 17)))

Barrier.append(Init_Barrier(A=(29+19, 6), B=(31+19, 17)))
Barrier.append(Init_Barrier(A=(19+19, 20), B=(22+19, 30)))

Barrier.append(Init_Barrier(A=(25+19, 20), B=(31+19, 25)))
Barrier.append(Init_Barrier(A=(34+19, 20), B=(37+19, 30)))


# 0 to 1
Barrier.append(Init_Barrier(A=(56, 0), B=(57, 6)))
Barrier.append(Init_Barrier(A=(56, 8), B=(57, 29)))

# 1
Barrier.append(Init_Barrier(A=(22+38, 0), B=(25+38, 11)))
Barrier.append(Init_Barrier(A=(31+38, 0), B=(34+38, 11)))
Barrier.append(Init_Barrier(A=(25+38, 0), B=(31+38, 3)))
Barrier.append(Init_Barrier(A=(25+38, 6), B=(26+38, 17)))


Barrier.append(Init_Barrier(
	A=(22+38, 13), B=(23+38, 14)))
Barrier.append(Init_Barrier(
	A=(22+38, 16), B=(23+38, 17)))

Barrier.append(Init_Barrier(
	A=(33+38, 13), B=(34+38, 14)))
Barrier.append(Init_Barrier(
	A=(33+38, 16), B=(34+38, 17)))


Barrier.append(Init_Barrier(A=(22+38, 0), B=(34+38, 11)))
Barrier.append(Init_Barrier(A=(25+38, 11), B=(31+38, 17)))

Barrier.append(Init_Barrier(A=(29+38, 6), B=(31+38, 17)))
Barrier.append(Init_Barrier(A=(19+38, 20), B=(22+38, 30)))

Barrier.append(Init_Barrier(A=(25+38, 20), B=(31+38, 25)))
Barrier.append(Init_Barrier(A=(34+38, 20), B=(37+38, 30)))





# 1 to 2
Barrier.append(Init_Barrier(A=(76, 0), B=(77, 6)))
Barrier.append(Init_Barrier(A=(76, 8), B=(77, 29)))


# 2
Barrier.append(Init_Barrier(A=(22+58, 0), B=(25+58, 11)))
Barrier.append(Init_Barrier(A=(31+58, 0), B=(34+58, 11)))
Barrier.append(Init_Barrier(A=(25+58, 0), B=(31+58, 3)))
Barrier.append(Init_Barrier(A=(25+58, 6), B=(26+58, 17)))


Barrier.append(Init_Barrier(
	A=(22+58, 13), B=(23+58, 14)))
Barrier.append(Init_Barrier(
	A=(22+58, 16), B=(23+58, 17)))

Barrier.append(Init_Barrier(
	A=(33+58, 13), B=(34+58, 14)))
Barrier.append(Init_Barrier(
	A=(33+58, 16), B=(34+58, 17)))


Barrier.append(Init_Barrier(A=(22+58, 0), B=(34+58, 11)))
Barrier.append(Init_Barrier(A=(25+58, 11), B=(31+58, 17)))

Barrier.append(Init_Barrier(A=(29+58, 6), B=(31+58, 17)))
Barrier.append(Init_Barrier(A=(19+58, 20), B=(22+58, 30)))

Barrier.append(Init_Barrier(A=(25+58, 20), B=(31+58, 25)))
Barrier.append(Init_Barrier(A=(34+58, 20), B=(37+58, 30)))


Barrier.append(Init_Barrier(
	A=(89, 0), B=(95,28)))



# 额外出口

myMap = Map(L=Length, W=Width, E=Exit, B=Barrier, F=Fire)


