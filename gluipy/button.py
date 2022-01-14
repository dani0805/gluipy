from typing import Optional

from gluipy.modifier import Border
from gluipy.text import Label


class Button(Border):

    def __init__(self, text: str, cache_id=None, font_name='San Francisco, Hevetica Neue, Helvetica, Sans Serif',
                 font_size=24, color=(210, 210, 210, 255), hover_color=(255, 255, 255, 255),
                 background_color=(10, 30, 100), hover_background_color=(30, 50, 120), padding=(12, 5, 12, 5), radius=12):
        self.cache_id = cache_id
        self.label = Label(text, f"{cache_id}-label", font_name=font_name,
                           font_size=font_size, color=color, padding=padding).background(background_color)
        super().__init__(self.label, radius=radius)
        self.not_hover_color = color
        self.hover_color = hover_color
        self.not_hover_background_color = background_color
        self.hover_background_color = hover_background_color
        self.hover = False
        self.dirty = None

    def on_mouse_motion(self, x, y, dx, dy):
        # print(self._x, x, self._x + self._w, self._y, x,self._y + self._h)
        self.hover = self._x < x < self._x + self._w and self._y < y < self._y + self._h

    def _state_hash(self) -> Optional[str]:
        state_dict = super(Button, self)._state_hash() + f"{str(self.hover)}"
        return state_dict

    def draw_content(self, x, y, w, h, batch):
        self.color = self.hover_color if self.hover else self.not_hover_color
        background_color = self.hover_background_color if self.hover else self.not_hover_background_color
        # cache old positions and sizes
        old_label = self.elements[0].elements[0]
        padding = list(old_label.padding)
        padding[3] -= int(old_label.font_size/4)
        self.elements[0] = Label(old_label.text, f"{self.cache_id}-label",
                                 font_name=old_label.font_name,
                                 font_size=old_label.font_size, color=self.color,
                                 padding=padding).background(background_color)
        super(Button, self).draw_content(x, y, w, h, batch)




