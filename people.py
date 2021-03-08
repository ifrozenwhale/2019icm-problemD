from MyMap import MoveTO
import numpy as np
import time
import math
import random
Outer_Size = 1
MoveTO = []

MoveTO.append(np.array([0, -1]))	# UP
MoveTO.append(np.array([-1, 0]))  # LEFT
MoveTO.append(np.array([1, 0]))		# RIGHT
MoveTO.append(np.array([0, 1]))		# DOWN

MoveTO.append(np.array([1, -1]))	
MoveTO.append(np.array([1, 1]))
MoveTO.append(np.array([-1, 1]))	
MoveTO.append(np.array([-1, -1]))	

class Person:
	# 速度可以进行修正
	# 按照文献中的模型进行求解
	Normal_Speed = 2
	
	def __init__(self, id, pos_x, pos_y, type = 0, lastForward = 0):
		self.id = id
		self.pos = (pos_x, pos_y)
		self.speed = Person.Normal_Speed
		self.savety = False
		self.type = type
		self.lastForward = lastForward
	def name(self):
		return "ID_"+str(self.id)

	def __str__(self):
		return  self.name() + " (%d, %d)" % (self.pos[0], self.pos[1])


class People:
	def __init__(self, cnt, myMap):
		self.list = []
		self.tot = cnt
		self.map = myMap
		# 某时刻 map 上站的人的个数
		# 反映人流密度
		self.rmap = np.zeros((myMap.Length+2, myMap.Width+2))
		# map 上总的经过人数
		# 热力图
		self.thmap = np.zeros(((myMap.Length+2), (myMap.Width+2)))
		# 动态场
		self.dmap = np.zeros(((myMap.Length+2), (myMap.Width+2)))

		# 
		# 
		# 
		#
		## 这里是完全随机的初始化人群的位置，实际上可以按照藏品的受欢迎程度来进行适当的加权
		for i in range(cnt):
			

			# pos_x, pos_y = myMap.Random_Valid_Point()
			if i <= cnt * 4/23:
				pos_x, pos_y = myMap.Random_Valid_Point_l(2)
			elif i <= cnt * 10/23:
				pos_x, pos_y = myMap.Random_Valid_Point_l(1)
			elif i <= cnt * 17/23:
				pos_x, pos_y = myMap.Random_Valid_Point_l(0)
			elif i <= cnt * 21/23:
				pos_x, pos_y = myMap.Random_Valid_Point_l(-1)
			else:
				pos_x, pos_y = myMap.Random_Valid_Point_l(-2)
			# pos_x, pos_y = myMap.Random_Valid_Point_l(-2)




			# if self.map.space[int(pos_x)][int(pos_y)] == float("inf"):
			# 	print("why it is not valid? " + str(self.map.space[int(pos_x)][int(pos_y)]))

			# if not self.map.Check_Valid(pos_x, pos_y):
			# 	print("why it is not valid? " + str(self.map.space[pos_x][pox_y]))
			
			while self.getMapValue(self.rmap, pos_x, pos_y) >= 4:
				pos_x, pox_y = myMap.Random_Valid_Point()
			type = random.random()
			
			self.list.append(Person(i+1, pos_x, pos_y, type))
			self.addMapValue(self.rmap, pos_x, pos_y)
			self.addMapValue(self.thmap, pos_x, pos_y)
			self.addMapValue(self.dmap, pos_x, pos_y)
	def setMapValue(self, mp, x, y, val=0):
		x, y = int(x), int(y)
		mp[x][y] = val

	def addMapValue(self, mp, x, y, add=1):
		if mp is self.rmap:
			x, y = int(x), int(y)
			try:
				mp[x][y] += add
			except IndexError:
				print("x = " + str(x) + " y = " + str(y))
		else:
			# if mp is self.thmap:
				#print("stop here x = " + str(x) + " and y = " + str(y))
			try:
				x, y = int(x), int(y)
				mp[x][y] += add
			except IndexError:
				print("x = " + str(x) + " y = " + str(y))

	def getMapValue(self, mp, x, y):
		x, y = int(x), int(y)
		return mp[x][y]



	def getSpeed(self, p, De):
		x, y = int(p.pos[0]), int(p.pos[1])
		gama = 0.5
		beta = -2 * (1 - gama) / (1 + pow(2.7, -1 * De)) - gama + 2
		# print(beta)
		# tot = 0
		# for dx in range(-1, 2):
		# 	for dy in range(-1, 2):
		# 		nx, ny = x+dx, y+dy
		# 		if self.map.Check_Valid(nx, ny):
		# 			tot += self.rmap[nx][ny]
		# # ratio = random.uniform(math.exp(-2*tot/(5*5)), 1.5*math.exp(-2*tot/(5*5)))
		# if tot<2:
		# 	ratio = random.uniform(1.1, 1.5)
		# elif tot<4:
		# 	ratio = random.uniform(0.9, 1.1)
		# elif tot<7:
		# 	ratio = random.uniform(0.9, 1.0)
		# else:
		# 	ratio = random.uniform(0.7, 0.9)
		# if  Person.Normal_Speed * beta >= 1:
		# 	print("Here beta = " + str(beta) + "speed too quick" + str(Person.Normal_Speed * beta ))
		return Person.Normal_Speed * beta

	def move(self, p, dire, show=False):
		# 移动
		if show:
			print(p, end=' ')
			print("to", end=' ')
		(now_x, now_y) = p.pos

		De = self.calDensityView(p, dire)
		speed = self.getSpeed(p, De)

		dx, dy= MoveTO[dire][0]*speed, MoveTO[dire][1]*speed
		next_x, next_y = int(p.pos[0] + dx), int(p.pos[1] + dy)
		if not self.map.Check_Valid(next_x, next_y):
			next_x, next_y = int(p.pos[0]+ MoveTO[dire][0]), int(p.pos[1] + MoveTO[dire][1])
		if self.map.Check_Valid(next_x, next_y):
			self.addMapValue(self.rmap, now_x, now_y, -1)
			self.addMapValue(self.rmap, next_x, next_y, 1)
			p.pos = (next_x, next_y)
		
		# print("before: " + str(p.pos))
		# print("the dx = " + str(dx) + " and dy = " +str(dy))
		# print("the speed == " + str(speed))
		
		# print("after: " + str(p.pos))
		# # print("but the next_x = " + str(next_x) + " and the next_y " + str(next_y))
		# print("----------------")

		if self.map.checkSavefy(p.pos):
			p.savety = True
			self.setMapValue(self.rmap, next_x, next_y, 0)
		if self.map.Check_Valid(next_x, next_y):
			addThVal = self.getMapValue(self.rmap, next_x, next_y)
			self.addMapValue(self.thmap, next_x, next_y, addThVal)
			self.addMapValue(self.dmap, next_x, next_y, addThVal)
		if show:
			print(p)




	def calDensityView(self, p, dire):
		# 视野范围为2PI，视距为r=5
		cntView = 0
		px = 0
		py = 0
		x, y = int(p.pos[0]), int(p.pos[1])
		for i in range(0, 5):
			for j in range(-2, 3):
				if dire == 0:
					px = x - i
					py = y + j
				elif dire == 1:
					px = x + j
					py = y - i
				elif dire == 2:
					px = x + i
					py = y + j
				elif dire == 3:
					px = x + j
					py = y + i
				else:
					pass
				if self.map.Check_Valid(px, py):
					cntView += self.rmap[px][py]

		for i in range(0, 5):
			for j in range(0, 5):
				if dire == 4:
					px = x + i
					py = y - j
				elif dire == 5:
					px = x + i 
					py = y + j
				elif dire == 6:
					px = x - i
					py = y + j 
				elif dire == 7:
					px = x - i
					py = y - j
				if self.map.Check_Valid(px, py):
					cntView += self.rmap[px][py]
		return cntView
	def run(self):
		cnt = 0
		for p in self.list:
			if p.savety:
				cnt = cnt + 1
				continue
			while not self.map.Check_Valid(p.pos[0], p.pos[1]):
				p.pos = self.map.Random_Valid_Point()
			# speed = p.speed #random.uniform(p.speed-0.1, p.speed+0.1)
			# (now_x, now_y) = p.pos
			choice = []
			weigh = []
			P = []
			tempP = []
			Dire = [0, 1, 2, 3, 4, 5, 6, 7]
			random.shuffle(Dire)
			Iij = 1
			speed = [0, 0, 0, 0, 0, 0, 0, 0]
			
			# debug
			cnt_stop = 0
			for dire in Dire:
				De = self.calDensityView(p, dire)
				speed[dire] = self.getSpeed(p, De)

				dx, dy = MoveTO[dire][0]*speed[dire], MoveTO[dire][1]*speed[dire]
				(next_x, next_y) = p.pos[0]+dx, p.pos[1]+dy
				(next_x_bd, next_y_bd) = MoveTO[dire][0] + p.pos[0], MoveTO[dire][1] + p.pos[1]
				# 下一步能走
				if self.map.Check_Valid(next_x, next_y) and self.getMapValue(self.rmap, next_x, next_y)<=10:
					
					# 计算静态场
					Sij = self.map.getDeltaP(p.pos, (next_x, next_y))
					# 计算转移概率
					#print(self.map.FireDegree[int(next_x)][int(next_y)])
					tempP.append(self.calTransPreP(p, Sij, self.map.FireDegree[int(next_x)][int(next_y)], Iij))
					# print("tmp = " + str(self.calTransPreP(p, Sij, 0, Iij)))
					# P.append(self.calTransPreP(p, Sij, 0, Iij))
					choice.append(dire)
					# weigh.append(self.map.getDeltaP(p.pos, (next_x, next_y)))
				elif self.map.Check_Valid(next_x_bd, next_y_bd) and self.getMapValue(self.rmap, next_x_bd, next_y_bd)<=10:
										
					# 计算静态场
					Sij = self.map.getDeltaP(p.pos, (next_x_bd, next_y_bd))
					# 计算转移概率
					tempP.append(self.calTransPreP(
						p, Sij, self.map.FireDegree[int(next_x_bd)][int(next_y_bd)], Iij))
					# print("tmp = " + str(self.calTransPreP(p, Sij, 0, Iij)))
					# P.append(self.calTransPreP(p, Sij, 0, Iij))
					choice.append(dire)
					# weigh.append(self.map.getDeltaP(p.pos, (next_x, next_y)))	
				else:
					cnt_stop += 1
					# if self.map.Check_Valid(next_x_bd, next_y_bd):
					# 	if self.getMapValue(self.rmap, next_x_bd, next_y_bd) <= 3:
					# 		print("THIS IS A STRANGE PROBLEM " + str(self.getMapValue(self.rmap, next_x_bd, next_y_bd)))
					if cnt_stop >= 8:
						for i in range(-1, 2):
							for j in range(-1, 2):
								px = p.pos[0] + i
								py = p.pos[1] + j
								#print("valid ? " + str(self.map.Check_Valid(px, py)) + str(self.getMapValue(self.rmap, px, py)))
							# print(self.getMapValue(self.rmap, px, py))
								# print("CANT GO THIS " + str(self.getMapValue(self.rmap, px, py)) + "valid ? " +
								# 	str(self.map.Check_Valid(px, py)) + str(self.map.space[int(px)][int(py)]))
						# print("CANT't GO to THIS because valid? " +
					    #   	str(self.map.Check_Valid(next_x_bd, next_y_bd)) + " or valid ? " + str(self.map.Check_Valid(next_x, next_y)) + "value ? " )
			if len(choice)>0:
				N = 0
				for tmp in tempP:
					N += tmp
				if N != 0:
					for tmp in tempP:
						P.append(tmp/N)
				else:
					for tmp in tempP:
						P.append(0)
				index = P.index(max(P))
				# print(P)
				x, y = int(p.pos[0]), int(p.pos[1])
				# if index == 0:
				# 	x, y = x-1, y
				# elif index == 1:
				# 	x, y = x, y-1
				# elif index == 2:
				# 	x, y = x+1, y
				# elif index == 3:
				# 	x, y = x, y+1
				# elif index == 4:
				# 	x, y = x+1, y-1
				# elif index == 5:
				# 	x, y = x+1, y+1
				# elif index == 6:
				# 	x, y = x-1, y+1
				# elif index == 7:
				# 	x, y = x-1, y-1
				# else: 
				# 	x, y = x, y

				if p.lastForward == index:
					Iij = 1.2
				else:
					Iij = 1
				
				(x, y) = (x, y) + MoveTO[index]					
				if p.type > self.map.CompeteStatus[x][y]:
					# print("self.map.CompeteStatus[x][y]" + str(self.map.CompeteStatus[x][y]))
					self.map.CompeteStatus[x][y] = p.type
					if random.random() >= 0.3:
						self.move(p, choice[index])

						# 更新动态场
						if self.map.Check_Valid(p.pos[0], p.pos[1]):
							self.addMapValue(self.dmap, p.pos[0], p.pos[1])

					else:
						self.addMapValue(self.thmap, p.pos[0], p.pos[1])
						#print("compete1")
						# print("here stop!! x = " + str(p.pos[0]) + " and y = " + str(p.pos[1]))
						pass
				elif p.type == self.map.CompeteStatus[x][y]:
					if random.random() >= 0.5:
						self.move(p, choice[index])
						# 更新动态场
						self.addMapValue(self.dmap, p.pos[0], p.pos[1])
					else:
						self.addMapValue(self.thmap, p.pos[0], p.pos[1])
						#print("compete2")
						# print("here stop!! x = " + str(p.pos[0]) + " and y = " + str(p.pos[1]))
						pass
				else:
					if random.random() >= 0.7:
						self.move(p, choice[index])
						self.addMapValue(self.dmap, p.pos[0], p.pos[1])
						# print("compete3 move")
					else:
						self.addMapValue(self.thmap, p.pos[0], p.pos[1])
						#print("compete3")
						# print("here stop!! x = " + str(p.pos[0]) + " and y = " + str(p.pos[1]))
						pass
				p.lastForward = index	
				p.speed = speed[index]
			else:
				self.addMapValue(self.thmap, p.pos[0], p.pos[1])
				print("NO chance")
				# print("here no choice! x = " + str(p.pos[0]) + " and y = " + str(p.pos[1]))
				# print("-------------------")
				# for i in range(-1,2):
				# 	for j in range(-1, 2):
				# 		px = p.pos[0] + i
				# 		py = p.pos[1] + j
				# 		# print(self.getMapValue(self.rmap, px, py))
				# 		print(str(self.getMapValue(self.rmap, px, py)) + "valid ? " + str(self.map.Check_Valid(px, py)) + str(self.map.space[int(px)][int(py)]))
				p.speed = 0

			if p.savety:
				cnt = cnt + 1
		# 下一个时间步，竞争重新计算，这里清空
		self.CompeteStatus = np.zeros((self.map.Length+Outer_Size*2, self.map.Width+Outer_Size*2))
		return cnt
	


	def calDij(self):
		# alpha 表示动态场的衰退概率, beta 表示扩散概率
		beta = 0.1 
		alpha = 0.2
		# now_x, now_y = int(p.pos[0]), int(p.pos[1])
		# for i in range(0, self.map.Width+2):
		# 	for j in range(0, self.map.Length+2):
		# 		if self.map.Check_Valid(i, j):
		# 			self.dmap[i][j] *= alpha

		self.dmap *= alpha
		for now_x in range(0, self.map.Width):
			for now_y in range(0, self.map.Length):
				
				for dx in range(-1, 2):
					for dy in range(-1, 2):
						px = now_x + dx
						py = now_y + dy
						if self.map.Check_Valid(px, py):
							self.dmap[px][py] *= (1 + beta)
							# self.dmap[now_x][now_y] *= alpha
							# if self.dmap[now_x][now_y] >= 100:
							# 	print("NOW Dij = " + str(self.dmap[now_x][now_y]))

	def calTransPreP(self, p, Sij, Fij, Iij):
		e = 2.7
		x, y = int(p.pos[0]), int(p.pos[1])
		Dij = 0
		nij = 0
		esij = 1
		try:
			Dij = self.dmap[x][y]
		except IndexError:
			print("now index x = " + str(x) + " and  y = " + str(y))
		ks = 0.8
		kd = 0.2
		kf = 0
		# print("------------" + str(p.pos))
		try:
			if self.rmap[x][y] > 5 and self.rmap[x][y] < 1000:
				nij = 1
			else:
				nij = 0
			if self.map.space[x][y] == float("inf"):
				esij = 0
			else:
				esij = 1
		except IndexError:
			print("x = " + str(x) + " y = " + str(y))
		# print(self.rmap[x][y])
		# print("nij = " + str(nij))
		# print("esij = " + str(esij))
		
		# N = 0
		# for i in range(0, self.map.Length):
		# 	for j in range(0, self.map.Width):
		# 		N += math.exp(ks * Sij) * math.exp(kd * Dij) / math.exp(kf * Fij) * Iij * (1 - nij) * esij

		# N = 1 / N
		pij = 0
		try:
			pij = math.exp(ks * Sij) * math.exp(kd * Dij) / math.exp(kf * Fij) * Iij * (1 - nij) * esij
		except OverflowError:
			# print("Sij = " + str(Sij) + " and Dij = " + str(Dij) + " and Fij = " + str(Fij))
			pass

		return pij
		

# Total_People = 2
# P = People(Total_People, myMap)


# Eva_Number = 0
# while Eva_Number<Total_People:
# 	Eva_Number = P.run()

	# time.sleep(0.5)
