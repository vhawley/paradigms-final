from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import sys
import os
import thread

import pygame
from math import *
from pygame.locals import *

class Player(pygame.sprite.Sprite):
	def __init__(self, gs=None, number=0, x=0, y=0, angle=0):
		self.gs = gs
		self.x = x
		self.y = y
		self.angle = angle
		self.maxhealth = 32.0
		self.health = self.maxhealth
		self.number = number

		self.baseimage = pygame.transform.scale(pygame.image.load("cars/" + self.gs.cars[self.number]),(100,100))
		self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(x, y)
		self.rect = self.rect.move(self.rect.width / -2, self.rect.height / -2)

	def tick(self):
		self.image = pygame.transform.rotate(self.baseimage, self.angle + 90)
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(self.x, self.y)
		self.rect = self.rect.move(self.rect.width / -2, self.rect.height / -2)

class Powerup:
	def __init__(self, gs=None, number=0, x=0, y=0):
		self.gs = gs
		self.number = number
		self.x = x
		self.y = y
		self.image = pygame.image.load("powerups/" + self.gs.powerupimages[self.number])
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(x, y)
		self.rect = self.rect.move(self.rect.width / -2, self.rect.height / -2)

class GameSpace:
	def __init__(self, lr, number):
		self.players = list()
		self.lr = lr
		self.playernumber = number
		self.cars = ["ambulance.png", "audi.png", "blackviper.png", "car.png", "minitruck.png", "minivan.png", "police.png", "taxi.png", "truck.png"]
		self.powerupimages = ["doubledamage.png", "health.png", "invuln.png", "speed.png"]
		self.powerups = list()
		self.gameover = 0
		self.winner = 0
		
	def main(self):
		# 1) basic init
		pygame.init()
		pygame.mixer.init()
		self.sounds = list()
		for i in range(1,5):
			self.sounds.append(pygame.mixer.Sound("sound/crash" + str(i) + ".wav"))
		self.debug = 0
		self.size = self.width, self.height = 1024, 768

		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		self.trackedinputs = [K_UP, K_DOWN, K_LEFT, K_RIGHT]

		self.keysheld = {}
		for tinput in self.trackedinputs:
			self.keysheld[tinput] = 0
		self.tickrate = 60
	
		# 2) set up game objects
		self.clock = pygame.time.Clock()
		

		# 3) start game loop
		while self.gameover == 0:
			# 4) regulate tick speed
			self.clock.tick(self.tickrate)

			# 5) handle user input events
			for event in pygame.event.get():
				# send relevant player inputs to server for processing
				if (event.type == KEYDOWN) or (event.type == KEYUP):
					if (event.key in self.trackedinputs):
						# only relevant inputs need to be sent to server
						self.lr.sendLine("INPUT," + str(self.playernumber) + "," + str(event.type) + "," + str(event.key))
						if (event.type == KEYDOWN):
							self.keysheld[event.key] = 1
						elif (event.type == KEYUP):
							self.keysheld[event.key] = 0
				if event.type == pygame.QUIT:
					sys.exit()

			# 6) ongoing behavior
			for player in self.players:
				player.tick()

			self.screen.fill(self.black)
			for player in self.players:
				if (player.health > 0):
					self.screen.blit(player.image, player.rect)
					healthpct = float(player.health) / player.maxhealth
					healthrect = Rect(player.x - 48, player.y - 48, healthpct * 97, 7)
					healthborder = Rect(player.x - 50, player.y - 50, 100, 10)
					if self.playernumber == player.number:
						pygame.draw.rect(self.screen,(255,255,255), healthborder, 2)
					else:
						pygame.draw.rect(self.screen,(0,0,255), healthborder, 2)
					if (healthpct < 0.20):
						pygame.draw.rect(self.screen,(255,0,0), healthrect, 0)
					else:
						pygame.draw.rect(self.screen,(0,255,0), healthrect, 0)
			for powerup in self.powerups:
				self.screen.blit(powerup.image, powerup.rect)

			pygame.display.flip()
		
		self.screen.fill(self.black)
		font = pygame.font.Font(None,36)
		if (self.winner == 1):
			endGameText = font.render("You won!", 1 , (255,255,255))
		else:
			endGameText = font.render("You lose!", 1 , (255,255,255))
		textrect = endGameText.get_rect()
		textrect.centerx = self.width / 2
		textrect.centery = self.height / 2
		self.screen.blit(endGameText, textrect)
		pygame.display.flip()
		while 1:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

##################################################

class BumperClient(LineReceiver):
	def __init__(self):
		self.state = "WAITING"
		self.playernumber = -1
		self.gs = None
	def lineReceived(self, line):
		line = line.strip()
		if (self.state == "WAITING"):
			self.playernumber = int(line)
			if self.playernumber == -1:
				sys.exit("Game full. Exiting...")
			self.state = "READY"
			self.gs = GameSpace(self, self.playernumber)
			
		elif (self.state == "READY" and line == "START"):
			thread.start_new_thread(self.gs.main, ())
			self.state = "PLAYING"
		elif (self.state == "PLAYING"):
			line = line.strip().split(',')
			if line[0] == "PLAYER":
				if (len(self.gs.players) <= int(line[1])):
					self.gs.players.append(Player(self.gs, int(line[1]), float(line[2]), float(line[3]), float(line[4])))
				else:
					self.gs.players[int(line[1])].x = float(line[2])
					self.gs.players[int(line[1])].y = float(line[3])
					self.gs.players[int(line[1])].angle = float(line[4])
				self.gs.players[int(line[1])].health = float(line[5])
				self.gs.players[int(line[1])].maxhealth = float(line[6])
			elif line[0] == "POWERUP":
				print line
				if line[1] == "START":
					self.gs.powerups = list()
				else:
					self.gs.powerups.append(Powerup(self.gs, int(line[1]), int(line[2]), int(line[3])))
			elif line[0] == "SOUND":
				self.gs.sounds[int(line[1])-1].play()
			elif line[0] == "GAMEEND":
				self.gs.gameover = 1
				winner = int(line[1])
				if winner == self.gs.playernumber:
					self.gs.winner = 1
					
		else:
			print line
		

class BumperClientFactory(ClientFactory):
	def buildProtocol(self, addr):
		newconn = BumperClient()
		return newconn

##################################################

myfactory = BumperClientFactory()

reactor.connectTCP('student00.cse.nd.edu', 40077, myfactory)

reactor.run()

