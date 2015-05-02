import sys
import os

import pygame
from math import *
from pygame.locals import *

class Player(pygame.sprite.Sprite):
	def __init__(self, gs=None, number=0, x=0, y=0, angle=0):
		self.gs = gs
		self.x = x
		self.y = y
		self.angle = angle
		self.collisionangle = self.angle
		self.number = number
		self.speed = 0
		self.acceleration = 3
		self.maxspeed = 8
		self.maxhealth = 32.0
		self.health = self.maxhealth
		self.hit = 0

		self.baseimage = pygame.transform.scale(pygame.image.load("cars/" + gs.cars[self.number]),(100,100))
		self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(x, y)
		self.rect = self.rect.move(self.rect.width / -2, self.rect.height / -2)

	def tick(self):
		if (self.hit == 1):
			self.speed = self.speed - 0.75 * float(self.acceleration) / float(gs.tickrate)
			if (self.speed <= 0):
				self.hit = 0
			deltax = self.speed * -1 * cos(radians(self.collisionangle))
			deltay = self.speed * sin(radians(self.collisionangle))
			if (not (self.x + deltax > gs.width - 20 or self.x + deltax < 20)):
				self.x = self.x + deltax
				if (gs.debug == 0):
					self.rect = self.rect.move(deltax, 0)
			if (not (self.y + deltay > gs.height - 20 or self.y + deltay < 20)):
				self.y = self.y + deltay
				if (gs.debug == 0):			
					self.rect = self.rect.move(0, deltay)
			newwidth, newheight = self.image.get_rect().width, self.image.get_rect().height
			self.rect = self.image.get_rect().move(self.x + newwidth/-2, self.y + newheight/-2)
		else:
			if (gs.keysheld[self.number][K_UP] == 1): #accelerate forward
				if (self.speed < 0):
					self.speed = min(self.speed + 2 * float(self.acceleration) / float(gs.tickrate), 0)
				elif (self.speed >= 0):
					self.speed = min(self.speed + float(self.acceleration) / float(gs.tickrate), self.maxspeed)
			if (gs.keysheld[self.number][K_DOWN] == 1): #brakes/reverse
				if (self.speed <= 0):
					self.speed = max(self.speed - float(self.acceleration) / float(gs.tickrate), -1 * self.maxspeed)
				elif (self.speed > 0):
					self.speed = max(self.speed - 2 * float(self.acceleration) / float(gs.tickrate), 0)
			elif (gs.keysheld[self.number][K_UP] == 0): #slow down
				if (self.speed < 0):
					self.speed = min(self.speed + 0.75 * float(self.acceleration) / float(gs.tickrate), 0)
				elif (self.speed > 0):
					self.speed = max(self.speed - 0.75 * float(self.acceleration) / float(gs.tickrate), 0)
			if (gs.keysheld[self.number][K_LEFT] == 1): #turn left
				if (self.speed >= 0):
					self.angle = (self.angle + 2) % 360
				else:
					self.angle = (self.angle - 2) % 360
				self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
			
			if (gs.keysheld[self.number][K_RIGHT] == 1): #turn right
				if (self.speed >= 0):
					self.angle = (self.angle - 2) % 360
				else:
					self.angle = (self.angle + 2) % 360
				self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
			newwidth, newheight = self.image.get_rect().width, self.image.get_rect().height
			self.rect = self.image.get_rect().move(self.x + newwidth/-2, self.y + newheight/-2)		
			deltax = self.speed * -1 * cos(radians(self.angle))
			deltay = self.speed * sin(radians(self.angle))
			if (not (self.x + deltax > gs.width - 20 or self.x + deltax < 20)):
				self.x = self.x + deltax
				if (gs.debug == 0):
					self.rect = self.rect.move(deltax, 0)
			if (not (self.y + deltay > gs.height - 20 or self.y + deltay < 20)):
				self.y = self.y + deltay
				if (gs.debug == 0):			
					self.rect = self.rect.move(0, deltay)
		
			if (gs.debug == 1 and self.number == 0):
				newx, newy = pygame.mouse.get_pos()
				self.x = newx
				self.y = newy
				self.rect = self.image.get_rect().move(self.x + newwidth/-2, self.y + newheight/-2)
		
class GameSpace:
	def getDistanceDifference(self, p1, p2): # returns distance between two player cars in pixels
		dif = sqrt(pow(p1.x-p2.x,2) + pow(p1.y-p2.y,2))
		return dif

	def getAngleDifference(self, p1, p2): # returns mathematically difference of two car angles (in degrees)
		return p1.angle - p2.angle

	def getAngleOfImpact(self, p1, p2): # returns angle of straight line between two cars (in degrees)
		return degrees(atan2(p1.y-p2.y, p1.x-p2.x))

	def detectCollisions(self):		
		for i in range(0,len(self.players)-1):
			for j in range(i+1,len(self.players)):
				distance = self.getDistanceDifference(self.players[i],self.players[j])
				if (distance < 75): # maximum distance difference that could be collision
					totalspeed = abs(float(self.players[i].speed + self.players[j].speed))
					
					if (totalspeed > 2 and self.players[i].hit == 0 and self.players[j].hit == 0):
						self.players[i].hit = 1
						self.players[j].hit = 1
					
						self.players[i].collisionangle = (float(self.players[j].speed) / totalspeed) * self.players[j].angle + (float(self.players[i].speed) / totalspeed) * self.players[i].angle
						self.players[j].collisionangle = 360 - (float(self.players[j].speed) / totalspeed) * self.players[j].angle + (float(self.players[i].speed) / totalspeed) * self.players[i].angle

						self.players[i].health = self.players[i].health - max(1,abs(self.players[j].speed))
						self.players[j].health = self.players[j].health - max(1,abs(self.players[i].speed))

						self.players[i].speed = 0.5 * totalspeed
						self.players[j].speed = 0.5 * totalspeed

						closerdistance = 75 - distance
					angledifference = self.getAngleDifference(self.players[i],self.players[j])
					impactangle = self.getAngleOfImpact(self.players[i],self.players[j])
					print angledifference, impactangle

					

	def main(self):
		# 1) basic init
		pygame.init()
		pygame.mixer.init()
		self.debug = 0
		self.size = self.width, self.height = 800, 600

		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		self.players = list()
		self.powerups = list()
		self.cars = ["ambulance.png", "audi.png", "blackviper.png", "car.png", "minitruck.png", "minivan.png", "police.png", "taxi.png", "truck.png"]
		self.trackedinputs = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
		

		self.playernumber = 0
		self.players.append(Player(self, self.playernumber, 300, 300, 270))
		self.players.append(Player(self, 1, 600, 300, 90))
		#get playernumber from server after connecting

		self.keysheld = list()
		for player in self.players:
			self.keysheld.append(dict())
			for key in self.trackedinputs:
				self.keysheld[player.number][key] = 0
		self.tickrate = 60

		pygame.key.set_repeat(1, 50)
	
		# 2) set up game objects
		self.clock = pygame.time.Clock()


		# 3) start game loop
		while 1:
			# 4) regulate tick speed
			self.clock.tick(self.tickrate)

			# 5) handle user input events
			for event in pygame.event.get():
				# send relevant player inputs to server for processing
				if ((event.type == KEYDOWN) and ((not event.key in self.trackedinputs) or (self.keysheld[self.playernumber][event.key] == 0))) or (event.type == KEYUP):
					if (event.key in self.trackedinputs):
						# only relevant inputs need to be sent to server
						print str(self.playernumber) + "," + str(event.type) + "," + str(event.key)
						if (event.type == KEYDOWN):
							self.keysheld[self.playernumber][event.key] = 1
						elif (event.type == KEYUP):
							self.keysheld[self.playernumber][event.key] = 0
				if event.type == pygame.QUIT:
					sys.exit()

			# 6) ongoing behavior
			for player in self.players:
				player.tick()
			self.detectCollisions()
			# get new messages from server and update player states
					
			# 7) animation
			self.screen.fill(self.black)
			#draw background
			#draw players
			for player in self.players:
				self.screen.blit(player.image, player.rect)
				healthborder = Rect(player.x - 50, player.y - 50, 100, 10)
				healthpct = float(player.health) / player.maxhealth
				healthrect = Rect(player.x - 48, player.y - 48, healthpct * 97, 7)
				pygame.draw.rect(self.screen,(255,255,255), healthborder, 2)
				if (healthpct < 0.20):
					pygame.draw.rect(self.screen,(255,0,0), healthrect, 0)
				else:
					pygame.draw.rect(self.screen,(0,255,0), healthrect, 0)
			#draw powerups
			#draw etc
			pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()



