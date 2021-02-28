import pygame
import random
from modules.utils import *

class NewAnimationException(Exception):
    def __init__(self, new_anim_name, pause_followup=False, *args):
        super().__init__(*args)
        self.next = new_anim_name
        self.pause_followup = pause_followup



class TriggerEvent(Exception):
    def __init__(self, trigger):
        super().__init__()
        self.trigger = trigger

class Animation():
    def __init__(self, spritesheet, **kwargs):

        self.followup = kwargs.get("followup", None)
        self.pause_followup = kwargs.get("pause_followup", False)

        self.paused = kwargs.get("paused", False)
        self.loop = kwargs.get("loop", True)

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


    def animate(self):
        if not self.paused:
            self.counter += 1
            if self.counter % self.framerate == 0:
                self.findex = (self.findex+1)
                if self.findex == len(self.frames) and self.loop:
                    self.findex = self.findex % len(self.frames)

                elif not self.loop and not self.followup:
                    self.paused = True
                
                elif self.findex == len(self.frames) and self.followup:
                    self.findex = 0
                    raise NewAnimationException(self.followup, self.pause_followup)

                self.counter = 0
        
            self.image = self.frames[self.findex]
    

class GameObject(pygame.sprite.Sprite):
    def __init__(self, animations: dict, starting_animation: str, *groups, **kwargs):

        self.rect = pygame.Rect(0,0,0,0)

        super().__init__(*groups)

        self.flipped = False

        self.live = not kwargs.get("start_dead", False)

        self.animations = animations
        self.change_animation(starting_animation)

        self.rect = self.image.get_rect()


    def update(self):
        try:
            self.animation.animate()
        except NewAnimationException as e:
            self.animation = self.animations[e.next]
            self.current_animation = e.next
            if e.pause_followup:
                self.animation.paused = True
        
        self.image = self.animation.image
        if self.flipped: self.image = pygame.transform.flip(self.image, True, False)

    def change_animation(self, animation):

        self.animation = self.animations[animation]
        self.current_animation = animation

        self.image = self.animation.frames[self.animation.findex]
        


class PhysicsObject(GameObject):
    def __init__(self, animations, starting_animation, *groups, **kwargs):

        self.set_colliders = PhysicsObject.default_hitbox


        if (custom_func := kwargs.get("set_colliders", None)):
            self.set_colliders = custom_func

        super().__init__(animations, starting_animation, *groups, **kwargs)


        


        self.is_trigger = kwargs.get("is_trigger", False)

        self.static = kwargs.get("static", False)
        if not self.static:
            self.gravity = 0
        

    def collidingBelow(self, physWorld):

        collidingWith = []
        toRaise = None

        for sprite in physWorld.sprites():
            if self.colliders["bottom"].colliderect(sprite.colliders["top"]):
                if not sprite.is_trigger:
                    collidingWith.append(sprite)
            if (self.colliders["bottom"].colliderect(sprite.colliders["top"]) or self.colliders["top"].colliderect(sprite.colliders["bottom"])) and sprite.is_trigger:
                toRaise = TriggerEvent(sprite)
        
        
        return collidingWith, toRaise

    

    def change_animation(self, animation):
        super().change_animation(animation)

        self.set_colliders(self, animation)

    def flip(self):
        self.flipped = not self.flipped
        self.set_colliders(self, self.current_animation)
        

    def default_hitbox(obj, *args):
        obj.colliders = {
            "top": pygame.Rect(0, 0, obj.image.get_width(), obj.image.get_height()/2).move(obj.rect.x, obj.rect.y),
            "bottom": pygame.Rect(0, obj.image.get_height()/2, obj.image.get_width(), obj.image.get_height()/2).move(obj.rect.x, obj.rect.y) 
        }
    

    def moveTo(self, x, y):
        self.rect = pygame.Rect(x, y, self.rect.w, self.rect.h)
        for collider in self.colliders:
            self.colliders[collider].move_ip(self.rect.x, self.rect.y)


    def moveBy(self, x, y):
        self.rect = pygame.Rect(self.rect.x + x, self.rect.y + y, self.rect.w, self.rect.h)
        for collider in self.colliders:

            coll = self.colliders[collider]

            self.colliders[collider] = pygame.Rect(coll.x + x, coll.y + y, coll.w, coll.h)


    def update(self, physWorld=None, *args, **kwargs):

        super().update(*args, **kwargs)

        if physWorld is None or self.static:
            return

        self.moveBy(0, self.gravity)
        try:
            coll, ex = self.collidingBelow(physWorld)
            if coll:
                if not self.current_animation == "idle" and not self.gravity == physWorld.gravity_acc: self.change_animation("idle")
                self.gravity = 0
            if ex:
                raise ex
        except TriggerEvent as e:
            pass
        finally:
            self.gravity += physWorld.gravity_acc
        
    
class StaticObject(PhysicsObject):
    def __init__(self, animations, starting_animation, *groups, **kwargs):
        def set_static_colliders(obj, animation):
            obj.colliders = {
                "top": pygame.Rect(0,0,obj.image.get_width(), obj.image.get_height()).move(obj.rect.x, obj.rect.y),
                "bottom": pygame.Rect(0,0,0,0).move(obj.rect.x, obj.rect.y)
            }
        
        self.set_colliders = kwargs.get("set_colliders", None)
        kwargs.pop("set_colliders", None)
        
        if self.set_colliders is None:
            self.set_colliders = set_static_colliders
        
        super().__init__(animations, starting_animation, *groups, set_colliders=self.set_colliders, static=True, **kwargs)


class Player(PhysicsObject):
    def __init__(self, animations, starting_animation, *groups, **kwargs):
        super().__init__(animations, starting_animation, *groups, **kwargs)

        self.damageCounter = 0
        self.health = 5
    
    def update(self, physWorld=None, *args, **kwargs):

        super().update(*args, **kwargs)

        self.damageCounter = max(0, self.damageCounter-1)

        if physWorld is None or self.static:
            return

        self.moveBy(0, self.gravity)
        try:
            coll, ex = self.collidingBelow(physWorld)
            if coll:
                if not self.current_animation == "idle" and not self.gravity == physWorld.gravity_acc: self.change_animation("idle")
                self.gravity = 0
            if ex:
                raise ex
        except TriggerEvent as e:
            if "enter" in e.trigger.animations:
                e.trigger.change_animation("enter")
                e.trigger.moveTo(random.randint(10, physWorld.display_surface.get_width()-10), random.randint(10, physWorld.display_surface.get_height()-100))
                if e.trigger.rect.x < physWorld.display_surface.get_width():
                    e.trigger.flip()
                elif e.trigger.flipped:
                    e.trigger.flip()

            if e.trigger.current_animation == "spikes" and self.damageCounter == 0:
                self.change_animation("hurt")
                self.health -= 1
                self.damageCounter = 120
            elif e.trigger.current_animation == "warn" and e.trigger.animations[e.trigger.current_animation].paused:
                e.trigger.animations[e.trigger.current_animation].paused = False
        finally:
            self.gravity += physWorld.gravity_acc


class DefaultPlayer(Player):
    def __init__(self, *groups, **kwargs):

        def default_player_hitboxes(obj, animation="idle"):

            

            if animation == "idle":
                obj.colliders = {
                    "top": pygame.Rect(3, 9, obj.image.get_width()-3, obj.image.get_height()-9).move(obj.rect.x, obj.rect.y),
                    "bottom": pygame.Rect(3, obj.image.get_height(), obj.image.get_width()-3, 4).move(obj.rect.x, obj.rect.y)
                }
            elif animation == "walk":
                if not obj.flipped:
                    obj.colliders = {
                        "top": pygame.Rect(3, 9, obj.image.get_width()-12, obj.image.get_height()-9).move(obj.rect.x, obj.rect.y),
                        "bottom": pygame.Rect(3, obj.image.get_height(), obj.image.get_width()-12, 4).move(obj.rect.x, obj.rect.y)
                    }
                else:
                    obj.colliders = {
                        "top": pygame.Rect(12, 9, obj.image.get_width()-12, obj.image.get_height()-9).move(obj.rect.x, obj.rect.y),
                        "bottom": pygame.Rect(12, obj.image.get_height(), obj.image.get_width()-12, 4).move(obj.rect.x, obj.rect.y)
                    }
            elif animation == "jump":
                if not obj.flipped:
                    obj.colliders = {
                        "top": pygame.Rect(1, 3, obj.image.get_width()-1, obj.image.get_height()-4).move(obj.rect.x, obj.rect.y),
                        "bottom": pygame.Rect(1, obj.image.get_height()-1, obj.image.get_width()-1, 4).move(obj.rect.x, obj.rect.y)
                    }
                else:
                    obj.colliders = {
                        "top": pygame.Rect(1, 3, obj.image.get_width()-1, obj.image.get_height()-4).move(obj.rect.x, obj.rect.y),
                        "bottom": pygame.Rect(1, obj.image.get_height()-1, obj.image.get_width()-1, 4).move(obj.rect.x, obj.rect.y)
                    }
        
        self.set_colliders = default_player_hitboxes

        player_animations = {
            "idle": Animation("player_idle", num_sprites=2),
            "jump": Animation("player_jump"),
            "walk": Animation("player_walk", num_sprites=6, framerate=10),
            "hurt": Animation("player_hurt", num_sprites=3, framerate=60, followup="idle")
        }

        super().__init__(player_animations, "idle", *groups, set_colliders=default_player_hitboxes, **kwargs)
    
    def change_animation(self, animation):
        super().change_animation(animation)

        if animation == "idle" and self.flipped:
            self.moveBy(9, 0)

        if animation == "walk" and self.flipped:
            self.moveBy(-6, 0)


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