import json

from pyglet import graphics

from gluipy.interface import UIElement


class CachedUIElement(UIElement):

    def __init__(self, x, y, w, h, sprite):
        self.sprite = sprite
        self.h = h
        self.w = w
        self.y = y
        self.x = x

    def draw(self, x: int, y: int, w: int, h: int, batch: graphics.Batch, cached=True):
        if self.w != w or self.h != h:
            return False
        self.x = x
        self.y = y
        self.sprite.x = x
        self.sprite.y = y
        self.sprite.batch = batch
        self.sprite.draw()
        return True


class Cache:
    object_cache = {}
    state_cache = {}

    @staticmethod
    def get_cached_uielement(object_dict, state_dict):
        object_hash = object_dict
        #if object_hash in Cache.object_cache.keys():
        try:
            current_state = Cache.object_cache[object_hash]
            state_hash = hash(state_dict)
            if current_state == state_hash:
                return Cache.state_cache[state_hash]
            else:
                del Cache.state_cache[current_state]
                del Cache.object_cache[object_hash]
                return None
        #else:
        except:
            return None

    @staticmethod
    def save_cache(object_dict, state_dict, x, y, w, h, sprite):
        object_hash = object_dict
        state_hash = hash(state_dict)
        if object_hash in Cache.object_cache.keys():
            current_state = Cache.object_cache[object_hash]
            try:
                del Cache.state_cache[current_state]
            except:
                pass
        Cache.object_cache[object_hash] = state_hash
        Cache.state_cache[state_hash] = CachedUIElement(x, y, w, h, sprite)



