import pygame
import os

from state import State

from pygame.constants import K_AT, K_a

# loads an image
def load_image(name):
    filepath = os.path.join("assets", "img", name)
    try:
        image = pygame.image.load(filepath)
    except pygame.error as error:
        # if this happens you are dumbass you are bumbling buffoon you are cretin you are fucking idioot and you need to try again because you are massive flaming dumbfuck
        print("Can't load image you dumbass you bumbling buffoon you cretin you fucking idiot try again you massive flaming dumbfuck:", name)
        raise SystemExit(error)
    image = image.convert()

    return image, image.get_rect()


def keyInput(event, state):

    if event.key == K_a:
        print("holy fuck! that's the a key!")
