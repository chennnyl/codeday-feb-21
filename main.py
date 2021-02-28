import random

import pygame
from pygame.locals import *
from pygame.sprite import Group

from modules.utils import *
from modules.objects import *

pygame.init()

toscale = pygame.Surface((720, 432))
screen = pygame.display.set_mode((1440, 864))

pygame.display.set_caption("pee n poo")
pygame.mouse.set_visible(1)

background = pygame.Surface(toscale.get_size())
background = background.convert()


clock = pygame.time.Clock()

world = PhysicsWorld(debug=False, display_surface=background)
otherObjects = Group()

ground1 = StaticObject({"ground": Animation("ground", colorkey=None)}, "ground")
ground2 = StaticObject({"ground": Animation("ground", colorkey=None)}, "ground")
ground1.moveTo(0, toscale.get_height() - ground1.image.get_height())
ground2.moveTo(ground1.image.get_width(), toscale.get_height() - ground1.image.get_height())

def spikeBoxes(obj, animation):
    obj.colliders = {
        "top": pygame.Rect(0,0,obj.image.get_width(), obj.image.get_height()-2).move(obj.rect.x, obj.rect.y),
        "bottom": pygame.Rect(0,obj.image.get_height()-2,obj.image.get_width(),8).move(obj.rect.x, obj.rect.y)
    }

spikes = StaticObject(
    {
        "warn": Animation("spikes_warn", num_sprites = 8, framerate=10, paused=True, followup="spikes", loop=False),
        "spikes": Animation("spikes", num_sprites=10, framerate=10, loop=False, followup="warn", pause_followup=True)
    }, "warn", start_dead=True, is_trigger=True, set_colliders=spikeBoxes
)
spikes.moveTo(0,toscale.get_height()-ground1.image.get_height()-spikes.image.get_height())

grasses = [
    GameObject({"grass": Animation("grass", num_sprites=9, framerate=10, start_frame=random.randint(0, 8))}, "grass", otherObjects) for _ in range(90) 
]
for i,grass in enumerate(grasses):
    grass.rect = pygame.Rect(grass.image.get_width()*i, toscale.get_height()-ground1.image.get_height()-grass.image.get_height(), grass.image.get_width(), grass.image.get_height())

player = DefaultPlayer(otherObjects)

enemy = PhysicsObject({
    "enter": Animation("enemy_entrance", num_sprites=9, framerate=10, followup="idle", loop=False),
    "idle": Animation("enemy_idle", num_sprites=4, framerate=20)
}, "enter", static=True, is_trigger=True)

world.add(player, ground1, ground2, spikes, enemy)

player.moveTo(background.get_width()/2, background.get_height()/2)
enemy.moveTo(4*background.get_width()/5, 3*background.get_height()/5)

running = True

direction = {"x": 0, "y": 0}

lastTime = 0
elapsed = 0
while running:
    elapsed += clock.tick(60)

    lastFlip = player.flipped

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYUP and event.key in (K_a, K_LEFT, K_d, K_RIGHT):
            direction["x"] = 0
            player.change_animation("idle")
            
        if event.type == pygame.KEYDOWN:

            if event.key in (K_w, K_SPACE):
                if player.gravity == world.gravity_acc:
                    player.change_animation("jump")
                    player.gravity = -8

            if event.key in (K_a, K_LEFT, K_d, K_RIGHT) and player.current_animation != "walk" and (player.gravity == world.gravity_acc or player.gravity == 0):
                player.change_animation("walk")

            if event.key in (K_a, K_LEFT):
                if not player.flipped:
                    player.flip()
                direction["x"] = -2
            if event.key in (K_d, K_RIGHT):
                if player.flipped:
                    player.flip()
                direction["x"] = 2
    
    player.moveBy(**direction)

    #background.fill((125, 233, 255))

    bg_image, _ = load_image("bg")

    background.blit(bg_image, (0,0))

    otherObjects.update()
    otherObjects.draw(background)

    world.update()
    world.draw(background)

    pygame.draw.rect(background, (255, 0, 0), pygame.Rect(10,10,20*player.health, 10))
    pygame.draw.rect(background, (200, 200, 255), pygame.Rect(125, 10, 300 - (300 *  (elapsed/(120*1000))), 10))
    

    toscale.blit(background, (0,0))
    pygame.transform.scale(toscale, (screen.get_size()), screen)

    pygame.display.update()