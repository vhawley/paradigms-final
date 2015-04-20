import sys
import os

import pygame
from math import *
from pygame.locals import *


class GameSpace:
	def main(self):
		# 1) basic init
		pygame.init()

		self.size = self.width, self.height = 800, 600

		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		pygame.key.set_repeat(1, 50)
	
		# 2) set up game objects
		self.clock = pygame.time.Clock()


		# 3) start game loop
		while 1:
			# 4) regulate tick speed
			self.clock.tick(60)

			# 5) handle user input events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

			# 6) ongoing behavior
								
			# 7) animation
			self.screen.fill(self.black)
			pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()



