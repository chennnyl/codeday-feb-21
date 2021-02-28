import pygame
from modules.utils import *

class SpriteSheet(pygame.sprite.Sprite):
    def __init__(self, spritesheet, *groups, **kwargs):
        super().__init__(*groups)

        self.live = not kwargs.get("start_dead", False)
        self.set_image(spritesheet, **kwargs)
    
    def set_image(self, spritesheet, **kwargs):
        num_sprites = kwargs.get("num_sprites", 1)
        self.framerate = kwargs.get("framerate", 30)

        

        colorkey = kwargs.get("colorkey", -1)

        self.spritesheet,_ = load_image(spritesheet, colorkey)

        sprite_width = self.spritesheet.get_width() / num_sprites
        sprite_height = self.spritesheet.get_height()

        self.frames = []
        for frame in range(num_sprites):
            self.frames.append(
                self.spritesheet.subsurface((frame * sprite_width, 0, sprite_width, sprite_height))
            )
        
        self.counter = 0
        self.findex = kwargs.get("start_frame", 0)
        self.image = self.frames[self.findex]


        self.rect = self.image.get_rect()

    def update(self):
        if self.live:
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

class PhysicsObject(SpriteSheet):
    def __init__(self, spritesheet, *groups, **kwargs):

        self.set_colliders = PhysicsObject.default_hitbox

        if (custom_func := kwargs.get("set_colliders", None)):
            self.set_colliders = custom_func

        super().__init__(spritesheet, *groups, **kwargs)


        self.static = kwargs.get("static", False)
        

    def set_image(self, spritesheet, *args, **kwargs):
        super().set_image(spritesheet, *args, **kwargs)

        self.set_colliders(self, *args)
        
    def default_hitbox(obj, *args):
        obj.colliders = {
            "top": (0, 0, obj.image.get_width(), obj.image.get_height()/2),
            "bottom": (0, obj.image.get_height()/2, obj.image.get_width(), obj.image.get_height()/2) 
        }
        
class StaticObject(PhysicsObject):
    def __init__(self, spritesheet, *groups, **kwargs):
        def set_static_colliders(obj):
            obj.colliders = {
                "top": (0,0,obj.image.get_width(), obj.image.get_height()),
                "bottom": (0,0,0,0)
            }
        
        super().__init__(spritesheet, *groups, set_colliders=set_static_colliders, static=True, **kwargs)


class Player(PhysicsObject):
    def __init__(self, spritesheet=None, *groups, **kwargs):
        super().__init__(spritesheet, *groups, **kwargs)


class DefaultPlayer(Player):
    def __init__(self, *groups, **kwargs):

        def default_player_hitboxes(obj, *args):
            if not args:
                obj.colliders = {
                    "top": (3, 9, obj.image.get_width()-3, 31),
                    "bottom": (3, 40, obj.image.get_width()-3, 2+obj.image.get_height()-40)
                }


        super().__init__("player_idle", *groups, num_sprites=2, set_colliders=default_player_hitboxes, **kwargs)


class PhysicsWorld(pygame.sprite.Group):
    def __init__(self, *sprites, **kwargs):
        super().__init__(*sprites)

        self.debug = kwargs.get("debug", False)
        self.display_surface = kwargs.get("display_surface", None)

    def add(self, *sprites):
        if any([True for sprite in sprites if not isinstance(sprite, PhysicsObject)]):
            raise TypeError("PhysicsWorld may only contain PhysicsObject or descendants")
    
        super().add(*sprites)
    
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)

        if self.debug:
            for sprite in self.sprites():
                for collider in sprite.colliders:
                    pygame.draw.rect(
                        self.display_surface, 
                        (0,255,0), 
                        pygame.Rect(*sprite.colliders[collider]).move(sprite.rect[0], sprite.rect[1]),
                        width = 2
                    )