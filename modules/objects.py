import pygame
from modules.utils import *

class SpriteSheet(pygame.sprite.Sprite):
    def __init__(self, spritesheet, *groups, **kwargs):
        super().__init__(*groups)

        self.set_image(spritesheet, **kwargs)
    
    def set_image(self, spritesheet, **kwargs):
        num_sprites = kwargs.get("num_sprites", 1)
        self.framerate = kwargs.get("framerate", 30)

        self.spritesheet,_ = load_image(spritesheet, -1)

        sprite_width = self.spritesheet.get_width() / num_sprites
        sprite_height = self.spritesheet.get_height()

        self.frames = []
        for frame in range(num_sprites):
            self.frames.append(
                self.spritesheet.subsurface((frame * sprite_width, 0, sprite_width, sprite_height))
            )
        
        self.image = self.frames[0]
        self.counter = 0
        self.findex = 0

    def update(self):
        self.counter += 1
        if self.counter % self.framerate == 0:
            self.findex = (self.findex+1) % len(self.frames)
            self.image = self.frames[self.findex]

            self.counter = 0        

        

    
        

    
    

class BaseBlock(pygame.sprite.Sprite):
    def __init__(self, color, dim, *groups):
        super().__init__(*groups)

        self.image = pygame.Surface((*dim,))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        
class Player(SpriteSheet):
    def __init__(self, spritesheet, *groups, **kwargs):
        super().__init__(spritesheet, *groups, **kwargs)