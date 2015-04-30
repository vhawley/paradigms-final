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
		self.number = number
		self.speed = 0
		self.acceleration = 3
		self.maxspeed = 8

		self.baseimage = pygame.transform.scale(pygame.image.load("cars/" + gs.cars[self.number]),(100,100))
		self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(x, y)
		self.rect = self.rect.move(self.rect.width / -2, self.rect.height / -2)

	def tick(self):
		if (gs.keysheld[K_UP] == 1): #accelerate forward
			if (self.speed < 0):
				self.speed = min(self.speed + 2 * float(self.acceleration) / float(gs.tickrate), 0)
			elif (self.speed >= 0):
				self.speed = min(self.speed + float(self.acceleration) / float(gs.tickrate), self.maxspeed)
		if (gs.keysheld[K_DOWN] == 1): #brakes/reverse
			if (self.speed <= 0):
				self.speed = max(self.speed - float(self.acceleration) / float(gs.tickrate), -1 * self.maxspeed)
			elif (self.speed > 0):
				self.speed = max(self.speed - 2 * float(self.acceleration) / float(gs.tickrate), 0)
		elif (gs.keysheld[K_UP] == 0): #slow down
			if (self.speed < 0):
				self.speed = min(self.speed + 0.75 * float(self.acceleration) / float(gs.tickrate), 0)
			elif (self.speed > 0):
				self.speed = max(self.speed - 0.75 * float(self.acceleration) / float(gs.tickrate), 0)
		if (gs.keysheld[K_LEFT] == 1): #turn left
			self.angle = self.angle + 1
			self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
			newwidth, newheight = self.image.get_rect().width, self.image.get_rect().height
			self.rect = self.image.get_rect().move(self.x + newwidth/-2, self.y + newheight/-2)
		if (gs.keysheld[K_RIGHT] == 1): #turn right
			self.angle = self.angle - 1
			self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
			newwidth, newheight = self.image.get_rect().width, self.image.get_rect().height
			self.rect = self.image.get_rect().move(self.x + newwidth/-2, self.y + newheight/-2)
		print self.angle
		deltax = self.speed * -1 * cos(radians(self.angle))
		deltay = self.speed * sin(radians(self.angle))
		if (not (self.x + deltax > gs.width - 20 or self.x + deltax < 20)):
			self.x = self.x + deltax
			self.rect = self.rect.move(deltax, 0)
		if (not (self.y + deltay > gs.height - 20 or self.y + deltay < 20)):
			self.y = self.y + deltay
			self.rect = self.rect.move(0, deltay)
		
class GameSpace:
	def main(self):
		# 1) basic init
		pygame.init()
		pygame.mixer.init()

		self.size = self.width, self.height = 800, 600

		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		self.players = list()
		self.powerups = list()
		self.cars = ["ambulance.png", "audi.png", "blackviper.png", "car.png", "minitruck.png", "minivan.png", "police.png", "taxi.png", "truck.png"]
		self.trackedinputs = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
		self.keysheld = {}
		for key in self.trackedinputs:
			self.keysheld[key] = 0
		self.tickrate = 60

		self.playernumber = 0
		self.players.append(Player(self, self.playernumber, 300, 300, 270))
		#get playernumber from server after connecting

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
				if ((event.type == KEYDOWN) and ((not event.key in self.keysheld) or (self.keysheld[event.key] == 0))) or (event.type == KEYUP):
					if (event.key in self.trackedinputs):
						# only relevant inputs need to be sent to server
						print str(self.playernumber) + "," + str(event.type) + "," + str(event.key)
						if (event.type == KEYDOWN):
							self.keysheld[event.key] = 1
						elif (event.type == KEYUP):
							self.keysheld[event.key] = 0
				if event.type == pygame.QUIT:
					sys.exit()

			# 6) ongoing behavior
			for player in self.players:
				player.tick()
			# get new messages from server and update player states
					
			# 7) animation
			self.screen.fill(self.black)
			#draw background
			#draw players
			for player in self.players:
				self.screen.blit(player.image, player.rect)
			#draw powerups
			#draw etc
			pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()



