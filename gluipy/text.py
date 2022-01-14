import math
import time
from typing import Any, Optional

from gluipy.base import BaseUIElement
from gluipy.interface import TextInputProtocol, AbstractDynamicCaret
import pyglet


class Label(BaseUIElement):
    h_compression_resistance = 500
    h_hugging_force = 500
    v_compression_resistance = 500
    v_hugging_force = 500

    def __init__(self, text, cache_id=None, font_name='San Francisco, Hevetica Neue, Helvetica, Sans Serif',
                 font_size=24, color=(40, 60, 60, 255), padding=(8, 5, 8, 5)):
        self.cache_id = cache_id
        self.padding = (padding[0], padding[1], padding[2], padding[3] + int(font_size/4))
        self.color = color
        self.font_size = font_size
        self.font_name = font_name
        self._text = text
        self.label = pyglet.text.Label(text, font_name=self.font_name, font_size=self.font_size, x=0, y=0,
                                       anchor_x='left', anchor_y='bottom', align='left', color=self.color, dpi=96)

    def _state_hash(self) -> Optional[str]:
        state_dict = f"{self.color}|{self._text}"
        return state_dict

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_value):
        self._text = new_value
        self.label.text = self._text

    def draw_content(self, x, y, w, h, batch):
        # print("#", end="")
        self.label.x = x + self.padding[0] + (w - self.label.content_width - (self.padding[0] + self.padding[2])) / 2
        self.label.y = y + self.padding[1] + (h - self.label.content_height - (self.padding[1] + self.padding[3])) / 2
        self.label.batch = batch
        self._x, self._y, self._w, self._h = x, y, w, h

    def size_requested(self) -> (int, int):
        self._w = self.label.content_width + self.padding[0] + self.padding[2]
        self._h = self.label.content_height + self.padding[1] + self.padding[3]
        return self._w, self._h


class DynamicCaret(AbstractDynamicCaret):

    def update_batch(self, batch: pyglet.graphics.Batch, color: (int, int, int)):
        r, g, b = color
        colors = (r, g, b, 255, r, g, b, 255)
        self._list = batch.add(2, pyglet.gl.GL_LINES, self._layout.background_group, 'v2f', ('c4B', colors))


class TextInput(BaseUIElement, TextInputProtocol):
    caching = False
    h_compression_resistance = 700
    h_hugging_force = 400
    v_compression_resistance = 780
    v_hugging_force = 700

    def __init__(self, *,
                 model: Any,
                 model_attribute: str,
                 cache_id,
                 font_name='San Francisco, Hevetica Neue, Helvetica, Sans Serif',
                 font_size=24,
                 length=30,
                 color=(40, 60, 60, 255)
                 ):
        self.cache_id = cache_id
        self._active = False
        self.color = color
        self.model = model
        self.model_attribute = model_attribute
        self.font_size = font_size
        self.font_name = font_name
        self.length = length
        self.document = pyglet.text.document.UnformattedDocument(getattr(model, model_attribute, ""))
        self.document.styles.setdefault("font_size", font_size)
        self.document.styles.setdefault("font_name", font_name)
        self.document.styles.setdefault("color", color)
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, 100, 20, wrap_lines=False)
        self.caret = DynamicCaret(self.layout, color=color[:3])
        self.caret.visible = True
        self._ref_label = pyglet.text.Label(
            "M"*self.length,
            font_name=self.font_name,
            font_size=self.font_size,
            x=0,
            y=0,
            anchor_x='left',
            anchor_y='bottom',
            align='left',
            color=self.color,
            dpi=96
        )

    def _state_hash(self) -> Optional[str]:
        return self.document.text

    def draw_content(self, x, y, w, h, batch):
        self.caret.update_batch(batch, self.color[:3])
        self.layout.batch = batch
        self.layout.x = x
        self.layout.y = y
        self.layout.width = w
        self.layout.height = h
        # drawing the caret
        # This is a quick hack, should really fix the pyglet caret drawing or reimplement text layouts from scratch
        if self._active:
            ts = time.time_ns() / (10 ** 9)
            ts = ts - math.floor(ts)
            cx, cy = self.layout.get_point_from_position(self.caret.position)
            pyglet.gl.glColor4f(self.color[0]/255, self.color[1]/255, self.color[2]/255, ts)
            font = self.document.get_font(max(0, self.caret._position - 1))
            batch.add(2, pyglet.gl.GL_LINES, None, ('v2f/dynamic', [cx + x, y - font.descent, cx + x, y + h]))
        self._x, self._y, self._w, self._h = x, y, w, h

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, new_value: bool):
        self._active = new_value

    def size_requested(self) -> (int, int):
        self._w = self._ref_label.content_width
        self._h = self._ref_label.content_height
        return self._w, self._h

    def _click(self, view):
        view.focus = self

        self._active = True

    def text_changed(self):
        setattr(self.model, self.model_attribute, self.document.text)
