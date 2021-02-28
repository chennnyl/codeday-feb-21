import random

import pygame
from pygame.locals import *
from pygame.sprite import Sprite, Group

from modules.utils import *
from modules.state import State
from modules.objects import DefaultPlayer, PhysicsWorld, StaticObject, SpriteSheet

pygame.init()

toscale = pygame.Surface((720, 432))
screen = pygame.display.set_mode((1440, 864))
pygame.display.set_caption("pee n poo")
pygame.mouse.set_visible(1)

background = pygame.Surface(toscale.get_size())
background = background.convert()



clock = pygame.time.Clock()

world = PhysicsWorld(debug=True, display_surface=background)
otherObjects = Group()

ground1 = StaticObject("ground", colorkey=None)
ground2 = StaticObject("ground", colorkey=None)
ground1.rect = (0, toscale.get_height() - ground1.image.get_height(), ground1.image.get_width(), ground1.image.get_height())
ground2.rect = (ground1.image.get_width(), toscale.get_height() - ground1.image.get_height(), ground2.image.get_width(), ground2.image.get_height())

spikes = SpriteSheet("spikes", otherObjects, num_sprites=17, framerate=10, start_dead=True)
spikes.rect = pygame.Rect(0,toscale.get_height()-ground1.image.get_height()-spikes.image.get_height(), spikes.image.get_width(), spikes.image.get_height())

grasses = [
    SpriteSheet("grass", otherObjects, num_sprites=9, framerate=10, start_frame=random.randint(0, 8)) for _ in range(90) 
]
for i,grass in enumerate(grasses):
    grass.rect = pygame.Rect(grass.image.get_width()*i, toscale.get_height()-ground1.image.get_height()-grass.image.get_height(), grass.image.get_width(), grass.image.get_height())

testPlayer = DefaultPlayer(otherObjects)

world.add(testPlayer, ground1, ground2)

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

    background.fill((125, 233, 255))

    world.update()
    world.draw(background)
    otherObjects.update()
    otherObjects.draw(background)

    toscale.blit(background, (0,0))
    pygame.transform.scale(toscale, (screen.get_size()), screen)

    pygame.display.update()