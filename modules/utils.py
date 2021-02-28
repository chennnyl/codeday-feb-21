import pygame
import os

from modules.state import State

from pygame.constants import K_AT, K_a, RLEACCEL

# loads an image
def load_image(name, colorkey=None):
    filepath = os.path.join("assets", "img", name + ".png")
    try:
        image = pygame.image.load(filepath)
    except pygame.error as error:
        # if this happens you are dumbass you are bumbling buffoon you are cretin you are fucking idioot and you need to try again because you are massive flaming dumbfuck
        print("Couldn't load image:", name)
        raise SystemExit(error)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()