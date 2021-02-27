import pygame
from pygame.locals import *
from pygame.transform import scale2x

from modules.utils import *
from modules.state import State
from modules.objects import Player

pygame.init()

toscale = pygame.Surface((720, 432))
screen = pygame.display.set_mode((1440, 864))
pygame.display.set_caption("pee n poo")
pygame.mouse.set_visible(1)

background = pygame.Surface(toscale.get_size())
background = background.convert()



clock = pygame.time.Clock()

playerGroup = pygame.sprite.RenderPlain()

testPlayer = Player("player_idle", playerGroup, num_sprites=2)
testPlayer.rect = (background.get_width()/2, background.get_height()/2)

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

    background.fill((255,0,0))

    playerGroup.update()
    playerGroup.draw(background)
    

    toscale.blit(background, (0,0))
    pygame.transform.scale(toscale, (screen.get_size()), screen)

    pygame.display.update()