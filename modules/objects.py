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

        self.is_trigger = kwargs.get("is_trigger", False)

        self.static = kwargs.get("static", False)
        if not self.static:
            self.gravity = 0
        

    def collidingBelow(self, physWorld):

        collidingWith = []

        for sprite in physWorld.sprites():
            if self.colliders["bottom"].colliderect(sprite.colliders["top"]):
                collidingWith.append(sprite)
        
        return collidingWith


    def set_image(self, spritesheet, *args, **kwargs):
        super().set_image(spritesheet, *args, **kwargs)

        self.set_colliders(self, *args)
        

    def default_hitbox(obj, *args):
        obj.colliders = {
            "top": pygame.Rect(0, 0, obj.image.get_width(), obj.image.get_height()/2),
            "bottom": pygame.Rect(0, obj.image.get_height()/2, obj.image.get_width(), obj.image.get_height()/2) 
        }
    

    def moveTo(self, x, y):
        self.rect = pygame.Rect(x, y, self.rect.w, self.rect.h)
        for collider in self.colliders:
            self.colliders[collider].move_ip(self.rect.x, self.rect.y)


    def moveBy(self, x, y):
        self.rect = pygame.Rect(self.rect.x + x, self.rect.y + y, self.rect.w, self.rect.h)
        for collider in self.colliders:
            self.colliders[collider].move_ip(x, y)


    def update(self, physWorld=None, *args, **kwargs):
        if physWorld is None or self.static:
            return

        self.moveBy(0, self.gravity)

        if self.collidingBelow(physWorld):
            self.gravity = 0
        self.gravity += physWorld.gravity_acc
        
    
class StaticObject(PhysicsObject):
    def __init__(self, spritesheet, *groups, **kwargs):
        def set_static_colliders(obj):
            obj.colliders = {
                "top": pygame.Rect(0,0,obj.image.get_width(), obj.image.get_height()),
                "bottom": pygame.Rect(0,0,0,0)
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
                    "top": pygame.Rect(3, 9, obj.image.get_width()-3, obj.image.get_height()-9),
                    "bottom": pygame.Rect(3, obj.image.get_height(), obj.image.get_width()-3, 4)
                }

        super().__init__("player_idle", *groups, num_sprites=2, set_colliders=default_player_hitboxes, **kwargs)


class PhysicsWorld(pygame.sprite.Group):
    def __init__(self, gravity_acc=0.25, *sprites, **kwargs):
        super().__init__(*sprites)

        self.gravity_acc = gravity_acc

        self.debug = kwargs.get("debug", False)
        self.display_surface = kwargs.get("display_surface", None)


    def add(self, *sprites):
        if any([True for sprite in sprites if not isinstance(sprite, PhysicsObject)]):
            raise TypeError("PhysicsWorld may only contain PhysicsObject or descendants")
        
        super().add(*sprites)


    def update(self, *args, **kwargs):
        [sprite.update(self, *args, **kwargs) for sprite in self.sprites()]


    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)

        if self.debug:
            for sprite in self.sprites():
                for collider in sprite.colliders:
                    pygame.draw.rect(
                        self.display_surface, 
                        (0,255,0), 
                        pygame.Rect(*sprite.colliders[collider]),
                        width = 2
                    )