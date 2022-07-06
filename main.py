import pygame
from pygame import mixer
import os
from random import randint
import sys
import time
from math import hypot

pygame.init()
pygame.font.init()
mixer.init()
screen = pygame.display.set_mode((800,300))
pygame.display.set_caption('Police Pursuit')
screen.fill((255,255,255))

def loadImg(image):
	return pygame.image.load(image).convert_alpha()

def midPoint(p1, p2):
	return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def CRCollision(rect, centreX, centreY, radius):
	"""detects collision between a rectangle and circle"""
	ctop, cbottom, cright, cleft = centreY + radius, centreY - radius, centreX + radius, centreX - radius

	if rect.right < cleft or rect.left > cright or rect.bottom > ctop or rect.top < cbottom:
		return False

	for x in (rect.left, rect.right):
		for y in (rect.bottom, rect.top):
			if hypot(x - centreX, y - centreY) <= radius:
				return True
	
	if rect.left <= centreX <= rect.right and rect.top <= centreY <= rect.bottom:
		return True

	return False

class Obstacle:
	def __init__(self):
		global activeObstacles, minX

		self.type = obstaclenames[randint(0, len(obstaclenames) - 1)].replace(".png", "")
		self.image = pygame.transform.scale(obstacles[self.type], (60, 60))
		self.y = randint(0, 2) * 100 +25
		self.x = 800
		self.getrect()

		withinX = [i for i in activeObstacles if i.x + 60 > self.x - minX]

		otherLanes = [25, 125, 225]
		otherLanes.remove(self.y)

		if bool([i for i in withinX if i.y == self.y]) or (bool([i for i in withinX if i.y == otherLanes[0]]) and bool([i for i in withinX if i.y == otherLanes[1]])):
			self.x += minX + 75


	def frame(self, amount): 
		self.x -= amount

	def getrect(self):
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x, self.y)

	def draw(self):
		self.getrect()
		pygame.Surface.blit(screen, self.image, self.rect)

class Police:
	def __init__(self):
		global frame, activePolice
		self.x = 800
		self.y = randint(0, 2) * 100 + 25
		self.start = frame
		self.getrect()

		otherLanes = [25, 125, 225]
		otherLanes.remove(self.y)
		if bool([i for i in activePolice if i.y == otherLanes[0]]) and bool([i for i in activePolice if i.y == otherLanes[1]]): 
			self.start += fps

	def getrect(self):
		global policecar
		self.rect = policecar.get_rect()
		self.rect.topleft = (self.x, self.y)
			
	def draw(self, alive):
		global frame, speed, policesuv, siren, fps
		if self.start + fps <= frame:
			if alive:
				self.x -= speed * 10
				self.getrect()
			pygame.Surface.blit(screen, policesuv, self.rect)

		else:
			pygame.Surface.blit(screen, siren, (750, self.y - 10)) 

class Clickable:
	hovered = False
	def __init__(self, text, pos, font, callback, args = None):
		self.text = text
		self.pos = pos
		self.font = font
		self.callback = callback
		self.args = args
		self.setRect()
		self.draw()

	def render(self):
		self.rend = self.font.render(self.text, True, self.getColour())

	def getColour(self):
		if bool(self.hovered):
			return (255, 255, 255)
		else:
			return (0, 0, 0)

	def setRect(self):
		self.render()
		self.rect = self.rend.get_rect()
		self.rect.center = self.pos

	def draw(self):
		self.render()
		screen.blit(self.rend, self.rect)

	def run(self):
		callback = self.callback
		if bool(self.args):
			callback(self.args)
		else:
			callback()

def deathScreen():
	global activeClickables, toDraw
	mixer.music.load('crashsound.wav')
	mixer.music.set_volume(1.8)
	mixer.music.play()
	font = pygame.font.SysFont("dejavuserif", 100)
	text = font.render("You crashed!", True, (255,255,0))
	textRect = text.get_rect()
	textRect.centerx = 400
	textRect.top = 25
	toDraw.append((text, textRect))

	font = pygame.font.SysFont("dejavuserif", 50)
	activeClickables = [Clickable("Play again", (400, 150), font, restart), Clickable("Exit", (400, 250), font, quit)]  

def restart():
	global speed, turnspeed, obstacleChance, frame, lane, laneframe, direction, activeObstacles, activeClickables, policeY, carX, carXChange, score, alive, toDraw, minX, activePolice, boompoint, paused

	song = "ES_Back to Where It Began - Rockin' For Decades.wav"
	# mixer.music.load(song) # this stopped
	# mixer.music.set_volume(0.4)
	# mixer.music.play(-1) 

	speed = 5 
	turnspeed = 7 
	obstacleChance = 90
	minX = 100

	frame = 1
	lane = 1
	laneframe = 1
	direction = 0
	activeObstacles = []
	activeClickables = []
	activePolice = []
	policeY = 100
	carX = 100
	carXChange = 0
	score = 0
	alive = True
	toDraw = []
	boompoint = ()
	paused = False

def pause():
	global activeClickables, toDraw, alive, paused
	paused = True
	alive = False
	font = pygame.font.SysFont("dejavuserif", 100)
	text = font.render("Paused", True, (255,255,0))
	textRect = text.get_rect()
	textRect.centerx = 400
	textRect.top = 25
	toDraw.append((text, textRect))

	font = pygame.font.SysFont("dejavuserif", 50)
	activeClickables = [Clickable("Resume", (400, 150), font, unpause), Clickable("Exit", (400, 250), font, quit)]

def unpause():
	global alive, toDraw, activeClickables, paused
	screen.fill((175, 175, 175))
	activeClickables = []
	toDraw = [] 
	alive = True
	paused = False

fps = 60
clock = pygame.time.Clock()
policecar = loadImg(os.path.join('images','police-car.png'))
robbercar = loadImg(os.path.join('images', 'robber-car.png'))
obstaclenames = os.listdir("images/obstacles")
obstacles = {i.replace(".png", ""): loadImg(os.path.join("images/obstacles", i)) for i in obstaclenames}

policecar = pygame.transform.scale(policecar, (75, 75))
robbercar = pygame.transform.scale(robbercar, (75, 75))
siren = pygame.transform.scale(loadImg(os.path.join("images", "siren.svg")), (50, 50))
siren = pygame.transform.rotate(siren, 90)
explosion = pygame.transform.scale(loadImg(os.path.join("images", "explosion.svg")), (75, 75))
policesuv = pygame.transform.flip(pygame.transform.scale(loadImg(os.path.join("images", "police-suv.svg")), (75, 75)), True, False)

obstacles['van'] = pygame.transform.flip(obstacles["van"], True, False)
pygame.display.set_icon(policecar)
restart()

def dw(): 
	global frame, lane, laneframe, direction, policeY, carX, run, score, obstacleChance, alive, activeClickables, activePolice, robbercar, boompoint

	carY = lane * 100 + 25 - (((frame - laneframe) * turnspeed - 100) * direction)

	screen.fill((175,175,175))

	if alive:
		if not bool(randint(0, obstacleChance)):
			activeObstacles.append(Obstacle())

	if alive and score >= 60:
		if not bool(randint(0, obstacleChance * 10)):
			activePolice.append(Police())

	if alive:
		if (carY + 50 > policeY and not bool(policeY % 100)) or (carY > policeY and bool(policeY % 100)):
			policeY += 1
		elif (carY - 50 < policeY and not bool(policeY % 100)) or (carY < policeY and bool(policeY % 100)):
			policeY -= 1

	for i in range(25):
		pygame.draw.line(screen, (255,255,255), (i * 40 - ((frame * speed) % 40),100), (i * 40 - ((frame * speed) % 40) + 30,100), 10)
		pygame.draw.line(screen, (255,255,255), (i * 40 - ((frame * speed) % 40),200), (i * 40 - ((frame * speed) % 40) + 30,200), 10)

	pygame.draw.line(screen, (0, 0, 0), (0, 0), (800, 0), 10)
	pygame.draw.line(screen, (0, 0, 0), (0, 300), (800,300), 10)

	carRect = robbercar.get_rect()
	carRect.topleft = (carX, carY)

	pygame.Surface.blit(screen, policecar, (0, policeY)) 
	pygame.Surface.blit(screen, robbercar, carRect)

	for i in activeObstacles:
		i.draw()
		if alive:
			i.frame(speed)
			if i.x < 0:
				activeObstacles.remove(i)
			if CRCollision(carRect, i.rect.centerx, i.rect.centery, 60):
				boompoint = midPoint(carRect.topleft, i.rect.topleft)
				alive = False
				deathScreen()

	for i in activePolice:
		i.draw(alive)

		if alive and bool(carRect.colliderect(i.rect)):
			boompoint = midPoint(carRect.topleft, i.rect.topleft)
			alive = False
			deathScreen()
	
	if not alive and bool(boompoint):
		pygame.Surface.blit(screen, explosion, boompoint)

	scorefont = pygame.font.SysFont("freesans", 50)
	scoreLabel = scorefont.render(str(score), 1, (0, 0, 0))
	scoreRect = scoreLabel.get_rect()
	scoreRect.right = 790
	scoreRect.top = 10
	screen.blit(scoreLabel, scoreRect)

	if (frame - laneframe) * turnspeed > 100: direction = 0

	for draw in toDraw:
		screen.blit(draw[0], draw[1])

	for i in activeClickables:

		if bool(i.rect.collidepoint(pygame.mouse.get_pos())):
			i.hovered = True
			if pygame.mouse.get_pressed()[0]:
				activeClickables = []
				i.run()
		else:
			i.hovered = False

		i.draw()

	pygame.display.update()

run = True
while run:
	pygame.event.get()
	dw()

	if not alive: 
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_p] and paused:
					unpause()
		continue 
	clock.tick(fps)	
	if carX > 750 or carX < 0:
		carXChange = 0
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key in [pygame.K_UP, pygame.K_w] and not bool(direction) and lane != 0:
				lane -= 1
				laneframe = frame
				direction = 1
			elif event.key in [pygame.K_DOWN, pygame.K_s] and not bool(direction) and lane != 2 or event.key == pygame.K_s and not bool(direction) and lane != 2:
				lane += 1
				laneframe = frame
				direction = -1

			if event.key in [pygame.K_RIGHT, pygame.K_d] and carX < 750:
				carXChange = speed
			elif event.key in [pygame.K_LEFT, pygame.K_a] and carX > 0:
				carXChange = -speed
			
			if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_p]:
				pause()	

		if event.type == pygame.KEYUP:

			if (event.key in [pygame.K_RIGHT, pygame.K_d] and carXChange> 0) or (event.key in [pygame.K_LEFT, pygame.K_a] and carXChange < 0):
				carXChange = 0
	carX += carXChange

	frame += 1
	if not bool(frame % fps):
		score += 1
		
		if not bool(score % 30):
			speed += max(round(10 / speed * 100)/100, 0.5)

			turnspeed += max(round(14 / turnspeed * 100) / 100, 0.5)

			obstacleChance -= max(round(900 / obstacleChance), 1) if obstacleChance > fps/4 else 0

			minX += max(round(100/minX), 1)

