from typing import Optional

from gluipy.base import BaseUIElement
from gluipy.container import BaseContainer

import pyglet


class Space(BaseUIElement):
    h_compression_resistance = 0
    h_hugging_force = 0
    v_compression_resistance = 0
    v_hugging_force = 0

    def _state_hash(self) -> Optional[str]:
        return ""

    def size_requested(self) -> (int, int):
        self._h = -self.container.gutter if self.container.direction == BaseContainer.V else 0
        self._w = -self.container.gutter if self.container.direction == BaseContainer.H else 0
        return self._w, self._h

    def draw(self, x: int, y: int, w: int, h: int, batch: pyglet.graphics.Batch, cached=False):
        self._x, self._y, self._w, self._h = x, y, w, h