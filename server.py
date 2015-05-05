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
		self.collisionangle = self.angle
		self.number = number
		self.speed = 0
		self.acceleration = 3
		self.maxspeed = 8
		self.maxhealth = 32.0
		self.health = self.maxhealth
		self.hit = 0

	def tick(self):
		if (self.hit == 1):
			self.speed = self.speed - 0.75 * float(self.acceleration) / float(self.gs.tickrate)
			if (self.speed <= 0):
				self.hit = 0
			deltax = self.speed * -1 * cos(radians(self.collisionangle))
			deltay = self.speed * sin(radians(self.collisionangle))
			if (not (self.x + deltax > self.gs.width - 20 or self.x + deltax < 20)):
				self.x = self.x + deltax
				if (self.gs.debug == 0):
					self.rect = self.rect.move(deltax, 0)
			if (not (self.y + deltay > self.gs.height - 20 or self.y + deltay < 20)):
				self.y = self.y + deltay
				if (self.gs.debug == 0):			
					self.rect = self.rect.move(0, deltay)

		else:
			if (self.gs.keysheld[self.number][K_UP] == 1): #accelerate forward
				if (self.speed < 0):
					self.speed = min(self.speed + 2 * float(self.acceleration) / float(self.gs.tickrate), 0)
				elif (self.speed >= 0):
					self.speed = min(self.speed + float(self.acceleration) / float(self.gs.tickrate), self.maxspeed)
			if (self.gs.keysheld[self.number][K_DOWN] == 1): #brakes/reverse
				if (self.speed <= 0):
					self.speed = max(self.speed - float(self.acceleration) / float(self.gs.tickrate), -1 * self.maxspeed)
				elif (self.speed > 0):
					self.speed = max(self.speed - 2 * float(self.acceleration) / float(self.gs.tickrate), 0)
			elif (self.gs.keysheld[self.number][K_UP] == 0): #slow down
				if (self.speed < 0):
					self.speed = min(self.speed + 0.75 * float(self.acceleration) / float(self.gs.tickrate), 0)
				elif (self.speed > 0):
					self.speed = max(self.speed - 0.75 * float(self.acceleration) / float(self.gs.tickrate), 0)
			if (self.gs.keysheld[self.number][K_LEFT] == 1): #turn left
				if (self.speed >= 0):
					self.angle = (self.angle + 2) % 360
				else:
					self.angle = (self.angle - 2) % 360
			
			if (self.gs.keysheld[self.number][K_RIGHT] == 1): #turn right
				if (self.speed >= 0):
					self.angle = (self.angle - 2) % 360
				else:
					self.angle = (self.angle + 2) % 360

			deltax = self.speed * -1 * cos(radians(self.angle))
			deltay = self.speed * sin(radians(self.angle))
			if (not (self.x + deltax > self.gs.width - 20 or self.x + deltax < 20)):
				self.x = self.x + deltax

			if (not (self.y + deltay > self.gs.height - 20 or self.y + deltay < 20)):
				self.y = self.y + deltay
		

class GameSpace:
	def __init__(self, factory):
		self.factory = factory
		self.players = list()
		self.cars = ["ambulance.png", "audi.png", "blackviper.png", "car.png", "minitruck.png", "minivan.png", "police.png", "taxi.png", "truck.png"]

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
					
						if (self.players[i].speed > self.players[j].speed):
							self.players[i].collisionangle = self.getAngleOfImpact(self.players[i],self.players[j])
							self.players[j].collisionangle = 360 - self.getAngleOfImpact(self.players[i],self.players[j])
						else:
							self.players[i].collisionangle = 360 - self.getAngleOfImpact(self.players[i],self.players[j])
							self.players[j].collisionangle = self.getAngleOfImpact(self.players[i],self.players[j])
						self.players[i].health = self.players[i].health - max(1,abs(self.players[j].speed))
						self.players[j].health = self.players[j].health - max(1,abs(self.players[i].speed))

						self.players[i].speed = 0.5 * totalspeed
						self.players[j].speed = 0.5 * totalspeed

						closerdistance = 75 - distance
					angledifference = self.getAngleDifference(self.players[i],self.players[j])
					impactangle = self.getAngleOfImpact(self.players[i],self.players[j])


					

	def main(self):
		# 1) basic init
		pygame.init()
		#pygame.mixer.init()
		self.debug = 0
		self.size = self.width, self.height = 800, 600

		self.black = 0, 0, 0

		#self.screen = pygame.display.set_mode(self.size)

		self.powerups = list()
		
		self.trackedinputs = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
		

		#get playernumber from server after connecting

		self.keysheld = list()
		for player in self.players:
			self.keysheld.append(dict())
			for key in self.trackedinputs:
				self.keysheld[player.number][key] = 0
		self.tickrate = 60
	
		# 2) set up game objects
		self.clock = pygame.time.Clock()


		# 3) start game loop
		while 1:
			# 4) regulate tick speed
			self.clock.tick(self.tickrate)

			# 6) ongoing behavior
			for player in self.players:
				player.tick()
			self.detectCollisions()


			for player in self.players:
				for client in self.factory.clients:
					client.sendLine("PLAYER," + str(player.number) + "," + str(player.x) + "," + str(player.y) + "," + str(player.angle) + "," + str(player.health) + "," + str(player.maxhealth))
			
			# get new messages from server and update player states
			

class GameLineReceiver(LineReceiver):
    def __init__(self,factory,gs):
        self.name = None
	self.factory = factory
        self.gs = gs
        self.state = "ADDPLAYER"        

    def connectionMade(self):
	if self.state == "ADDPLAYER":
            self.handle_ADDPLAYER()
        else:
            self.handle_PLAY()	
	
    def connectionLost(self,reason):
	print "connection lost. remove player from game"

    def lineReceived(self, line):
    	print line
	line = line.strip().split(',')
	if line[0] == "INPUT":
		playnum = int(line[1])
		keyevent = int(line[2])
		key = int(line[3])
		self.gs.keysheld[playnum][key] = -1 * (keyevent - 3) #1 if 2, 0 if 3

    def handle_ADDPLAYER(self):
        ## data received is used for creating a new player in the game
        ## set name
        if (len(self.gs.players) == 0):
        	self.gs.players.append(Player(self.gs, len(self.gs.players), len(self.gs.players) / 8 * 700, 300, 270))
        elif (len(self.gs.players) >= 1):
        	self.gs.players.append(Player(self.gs, len(self.gs.players), len(self.gs.players) / 8 * 700, 300, 270))
        	self.state = "PLAY"
        	thread.start_new_thread(self.gs.main, ())
        self.sendLine(str(len(self.gs.players) - 1))
	if (len(self.gs.players) >= 2):
		for client in self.factory.clients:
			client.sendLine("START")

    def handle_PLAY(self):
    	if (len(self.gs.players) >= 0 and len(self.gs.players) < 8):
        	self.gs.players.append(Player(self.gs, len(self.gs.players), len(self.gs.players) / 8 * 700, 300, 270))
        	self.sendLine(str(len(self.gs.players) - 1))
        else:
		self.sendLine("-1") #cannot join game... full

class GameFactory(Factory):
    def __init__(self):
        self.gs = GameSpace(self)
	self.clients = list()

    def buildProtocol(self,addr):
	self.clients.append(GameLineReceiver(self, self.gs))
        return self.clients[len(self.clients)-1]

reactor.listenTCP(26482, GameFactory())
reactor.run()

