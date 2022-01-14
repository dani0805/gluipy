import math
from math import pi, floor, ceil
from typing import Optional

from gluipy.base import ModifierMeta, ModifierProtocolMeta, BaseUIElement
from gluipy.interface import UIElement
from gluipy.container import BaseContainer
from pyglet.graphics import draw, Batch
from pyglet import gl, shapes, graphics
from pyglet.shapes import Line, Arc


class Border(BaseContainer, metaclass=ModifierProtocolMeta):
    direction = BaseContainer.H
    start_angles = {"sw": pi, "se": - pi / 2, "ne": 0.0, "nw": pi / 2}

    def __init__(self, element, thickness=2, radius=6, color=(100, 120, 120)):
        cache_id = element.cache_id + "P"
        super(Border, self).__init__([element], cache_id)
        self.cache_id = element.cache_id + "B"
        self.color = color
        self.radius = radius
        self.thickness = thickness
        self.h_compression_resistance = element.h_compression_resistance
        self.h_hugging_force = element.h_hugging_force
        self.v_compression_resistance = element.v_compression_resistance
        self.v_hugging_force = element.v_hugging_force
        self.shapes = []

    def size_requested(self) -> (int, int):
        self._w, self._h = super(Border, self).size_requested()
        self._w += self.thickness * 2
        self._h += self.thickness * 2
        return self._w, self._h

    def _state_hash(self) -> Optional[str]:
        state_dict = super(Border, self)._state_hash() + f"|{self.color}|{self.radius}|{self.thickness}"
        return state_dict

    def draw_content(self, x, y, w, h, batch):
        self.shapes = []
        gl.glEnable(gl.GL_STENCIL_TEST)
        gl.glStencilMask(0xFF)
        gl.glDepthMask(0x00)
        gl.glClearStencil(0)
        gl.glClear(gl.GL_STENCIL_BUFFER_BIT)
        gl.glColorMask(gl.GL_FALSE, gl.GL_FALSE, gl.GL_FALSE, gl.GL_FALSE)
        gl.glStencilFunc(gl.GL_ALWAYS, 1, 0xFF)
        gl.glStencilOp(gl.GL_KEEP, gl.GL_REPLACE, gl.GL_REPLACE)
        gl.glColor4f(1, 0, 0, 1.0)
        self._draw_mask(x + self.thickness,
                        y + self.thickness,
                        w - 2 * self.thickness,
                        h - 2 * self.thickness,
                        max(self.radius - self.thickness, 0))
        gl.glColorMask(gl.GL_TRUE, gl.GL_TRUE, gl.GL_TRUE, gl.GL_TRUE)
        gl.glStencilMask(0x00)
        gl.glDepthMask(0xFF)
        gl.glStencilFunc(gl.GL_EQUAL, 1, 0xFF)
        gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_KEEP)

        new_batch = Batch()
        # _h _w are use to cache the original requested size, if we do not subtract the thickness super.draw
        # will assume that we got less space and squeeze the content
        self._w -= 2 * self.thickness
        self._h -= 2 * self.thickness
        self.draw_elements(x, y, w, h, new_batch)
        new_batch.draw()
        gl.glStencilFunc(gl.GL_NOTEQUAL, 1, 0xFF)
        gl.glColor4f(self.color[0]/255, self.color[1]/255, self.color[2]/255, 1.0)

        self._draw_mask(x, y, w, h, self.radius)

        gl.glDisable(gl.GL_STENCIL_TEST)

        # for k in self.start_angles:
        #     self.shapes += list(self._draw_arc(x, y, w, h, k, new_batch))
        # for p in ["s", "w", "n", "e"]:
        #     self.shapes.append(self._draw_line(x, y, w, h, p, new_batch))

        self._x, self._y, self._w, self._h = x, y, w, h

    def draw_elements(self, x, y, w, h, batch):
        self.elements[0].draw(x + self.thickness, y + self.thickness, w - 2 * self.thickness, h - 2 * self.thickness,
                              batch, False)

    def _add(self, v1: (float, float), v2: (float, float)) -> (float, float):
        return v1[0] + v2[0], v1[1] + v2[1]

    def _draw_mask(self, x, y, w, h, r):
        v_list = []
        center = (x + w / 2, y + h / 2)
        mods = [(-r, 0), (0, r), (r, 0), (0, -r)]
        s_corners = [(x + r, y + r), (x + r, y + h - r), (x + w - r, y + h - r), (x + w - r, y + r)]
        e_corners = s_corners[1:] + s_corners[:1]
        for section, (c1, c2, mod) in enumerate(zip(s_corners, e_corners, mods)):
            v_list += [
                *self._add(c1, mod),
                *self._add(c2, mod),
                *center
            ]
            if r >= 1.0:
                subs = ceil(r)
                theta_sub = pi / 2 / (subs)
                theta_offset = - section * pi / 2 - pi
                for i in range(0, subs):
                    v_list += [
                        *self._add(c2, (
                        r * math.cos(theta_offset - i * theta_sub), r * math.sin(theta_offset - i * theta_sub))),
                        *self._add(c2, (r * math.cos(theta_offset - (i + 1) * theta_sub),
                                        r * math.sin(theta_offset - (i + 1) * theta_sub))),
                        *center
                    ]
        # v_list += v_list[-4:-2] + v_list[:2] + v_list[-2:]
        v_list = v_list[:2] + v_list + v_list[-2:]
        draw(int(len(v_list) / 2), gl.GL_TRIANGLE_STRIP, ('v2f', v_list))


class OnClick(BaseContainer, metaclass=ModifierProtocolMeta):
    direction = BaseContainer.H

    def __init__(self, element, clickfunc):
        cache_id = element.cache_id + "C"
        super(OnClick, self).__init__([element], cache_id)
        self._click = clickfunc


class Background(BaseContainer, metaclass=ModifierProtocolMeta):
    direction = BaseContainer.H
    background_opacity = 255

    def __init__(self, element, background_color):
        cache_id = element.cache_id + "P"
        super(Background, self).__init__([element], cache_id)
        self.background_color = background_color

    def _state_hash(self) -> Optional[str]:
        state_dict = super(Background, self)._state_hash() + f"|{self.background_color}"
        return state_dict

    def draw_content(self, x, y, w, h, batch):
        self._x, self._y, self._w, self._h = x, y, w, h
        if self.background_color is not None:
            self.backdrop = shapes.Rectangle(x, y, w, h, self.background_color)
            self.backdrop.opacity = self.background_opacity
            self.backdrop.draw()
        self.elements[0].draw(x, y, w, h, batch, False)


class Padding(BaseContainer, metaclass=ModifierProtocolMeta):
    direction = BaseContainer.H
    background_opacity = 255

    def __init__(self, element: UIElement, padding):
        cache_id = element.cache_id + "P"
        super(Padding, self).__init__([element], cache_id)
        self.padding = padding

    def _object_hash(self) -> Optional[dict]:
        hash_dict = super(Padding, self)._object_hash()
        hash_dict.update({"padding_modifier": True})
        return hash_dict

    def _state_hash(self) -> Optional[dict]:
        state_dict = super(Padding, self)._state_hash() + f"|{self.padding}"
        return state_dict

    def size_requested(self) -> (int, int):
        w, h = self.elements[0].size_requested()
        self._w = w + self.padding[0] + self.padding[2]
        self._h = h + self.padding[1] + self.padding[3]
        return self._w, self._h

    def draw_content(self, x: int, y: int, w: int, h: int, batch: graphics.Batch):
        self._x, self._y, self._w, self._h = x, y, w, h
        self.elements[0].draw(x + self.padding[0],
                              y + self.padding[1],
                              w - self.padding[0] - self.padding[2],
                              h - self.padding[1] - self.padding[3],
                              batch, False)


