import numpy as np
from queue import Queue
import random

Direction = {
	"RIGHT": 0, "UP": 1, "LEFT": 2, "DOWN": 3, "NONE": -1
}

MoveTO = []

MoveTO.append(np.array([0, -1]))  # UP
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

	if P1[0] == P2[0]:
		x = P1[0]
		for y in range(P1[1], P2[1]+1):
			exit.append((x, y))
	elif P1[1] == P2[1]:
		y = P1[1]
		for x in range(P1[0], P2[0]+1):
			exit.append((x, y))
	# 斜线
	else:
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
	if A[0] > B[0]:
		A, B = B, A

	x1, y1 = A[0], A[1]
	x2, y2 = B[0], B[1]

	if y1 < y2:
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
		self.CompeteStatus = np.zeros(
			(self.Length+Outer_Size*2, self.Width+Outer_Size*2))
		# 威胁场
		self.Fire = F
		self.FireDegree = np.zeros(
			((self.Length+Outer_Size*2), (self.Width+Outer_Size*2)))
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
			if ex == self.Length:
				self.space[ex+1][ey] = 1
			if ey == self.Width:
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
		if x > self.Length+1 or x < 0 or y > self.Width+1 or y < 0:
			return False

		if self.space[x][y] == float("inf"):
			return False
		else:
			return True

	def checkSavefy(self, pos):
		x, y = int(pos[0]), int(pos[1])
		if x == self.Length+1:
			x -= 1
		elif x == -1:
			x += 1
		if y == self.Width+1:
			y -= 1
		elif y == -1:
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
				if self.Check_Valid(i, j) and minDis[i][j] <= line:
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
				if self.Check_Valid(nx, ny) and tmpDis[nx][ny] == 0:
					queue.put((nx, ny))
					tmpDis[nx][ny] = dis + (1.0 if i < 4 else 1.4)  # 0 1 2 3 表示上下左右

		return tmpDis

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
Length = int(190 / 4)
Width = int(280 / 4)

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
Exit = Init_Exit(P1=(int(55/4), int(120/4)), P2=(int(55/4), int(150/4)))
Exit.extend(Init_Exit(P1=(int(70/4), int(178/4)), P2=(int(100/4), int(178/4))))
Exit.extend(Init_Exit(P1=(int(130/4), int(120/4)),
                      P2=(int(130/4), int(150/4))))
# Exit.extend(Init_Exit(
# 	P1=(int(30/4), int(230/4)), P2=(int(35/4), int(230/4))))
# Fire

# Fire = Init_Fire(P1=(int(80/4), int(190/4)), P2=(int(85/4), int(190/4)))
Fire = Init_Fire(P1=(int(40/4), int(230/4)), P2=(int(50/4), int(230/4)))
# 障碍 矩形区域
Barrier = list()
# Barrier.append(Init_Barrier(A=(0, 5), B=(30, 7)))
# Barrier.append(Init_Barrier(A=(10, 6), B=(15, 8)))


# Barrier.append(Init_Barrier(A=(0, 0), B=(int(30/4), int(196/4))))
# Barrier.append(Init_Barrier(A=(int(30/4), int(112/4)), B=(int(60/4), int(280/4))))
# Barrier.append(Init_Barrier(A=(int(120/4), int(112/4)), B=(int(150/4), int(280/4))))
# Barrier.append(Init_Barrier(A=(int(60/4), int(int(168/4))), B=(int(120/4), int(196/4))))
# Barrier.append(Init_Barrier(A=(int(60/4), int(252/4)), B=(int(120/4), int(280/4))))
# Barrier.append(Init_Barrier(A=(int(150/4), 0), B=(int(180/4), int(196/4))))

Barrier.append(Init_Barrier(A=(int(30/4), 0), B=(int(60/4), int(112/4))))
Barrier.append(Init_Barrier(A=(int(120/4), 0), B=(int(150/4), int(112/4))))
Barrier.append(Init_Barrier(A=(int(60/4), 0), B=(int(120/4), int(28/4))))
Barrier.append(Init_Barrier(
	A=(int(60/4), int(56/4)), B=(int(75/4), int(168/4))))


# 25 120	25 145
# 40 145	40 172
# 局部障碍
Barrier.append(Init_Barrier(
	A=(int(30/4), int(130/4)), B=(int(45/4), int(144/4))))
Barrier.append(Init_Barrier(
	A=(int(30/4), int(158/4)), B=(int(45/4), int(172/4))))

Barrier.append(Init_Barrier(
	A=(int(140/4), int(130/4)), B=(int(155/4), int(144/4))))
Barrier.append(Init_Barrier(
	A=(int(140/4), int(158/4)), B=(int(155/4), int(172/4))))


Barrier.append(Init_Barrier(
	A=(int(30/4), int(0/4)), B=(int(150/4), int(112/4))))
Barrier.append(Init_Barrier(
	A=(int(60/4), int(112/4)), B=(int(120/4), int(168/4))))

Barrier.append(Init_Barrier(
	A=(int(105/4), int(56/4)), B=(int(120/4), int(168/4))))
Barrier.append(Init_Barrier(
	A=(int(0/4), int(196/4)), B=(int(30/4), int(280/4))))

Barrier.append(Init_Barrier(
	A=(int(60/4), int(int(196/4))), B=(int(120/4), int(252/4))))
Barrier.append(Init_Barrier(
	A=(int(150/4), int(196/4)), B=(int(180/4), int(280/4))))
# Barrier.append(Init_Barrier(A=(int(150/4), 0), B=(int(180/4), int(196/4))))
# Barrier.append(Init_Barrier(A=(int(35/4), int(240/4)), B=(int(50/4), int(225/4))))


myMap = Map(L=Length, W=Width, E=Exit, B=Barrier, F=Fire)
