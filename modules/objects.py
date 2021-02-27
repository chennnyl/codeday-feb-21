import pygame

class BaseBlock(pygame.sprite.Sprite):
    def __init__(self, color, dim, *groups):
        super().__init__()

        self.image = pygame.Surface((*dim,))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        
        [self.add(group) for group in groups]
            

class Player(BaseBlock):
    def __init__(self, *groups):
        super().__init__((0, 255, 0),  (24, 48), *groups)