import pygame
from pygame.locals import *

from utils import *
from state import State
from objects import Player

pygame.init()

screen = pygame.display.set_mode((512, 512))
pygame.display.set_caption("pee n poo")
pygame.mouse.set_visible(1)

background = pygame.Surface(screen.get_size())
background = background.convert()

clock = pygame.time.Clock()

playerGroup = pygame.sprite.RenderPlain()

testPlayer = Player(playerGroup)

running = True

gameState = State(State.ACTION)

lastTime = 0
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keyInput(event, gameState)

    background.fill((0,0,0))

    playerGroup.draw(background)

    screen.blit(background, (0,0))
    
    pygame.display.update()