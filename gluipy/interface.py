from abc import ABC, abstractmethod
from typing import Protocol, Optional, Any

import pyglet


class UIElement(Protocol):
    container: "Container"
    h_compression_resistance: int
    h_hugging_force: int
    v_compression_resistance: int
    v_hugging_force: int
    _x: Optional[int]
    _y: Optional[int]
    _w: Optional[int]
    _h: Optional[int]

    def draw(self, x: int, y: int, w: int, h: int, batch: pyglet.graphics.Batch, cached=False) -> bool:
        pass

    def size_requested(self) -> (int, int):
        pass

    def click(self, x, y, button, modifiers, view) -> bool:
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass


class Container(UIElement, Protocol):
    elements: [UIElement]
    gutter: int
    direction: str


class AbstractDynamicCaret(pyglet.text.caret.Caret, ABC):

    @abstractmethod
    def update_batch(self, batch: pyglet.graphics.Batch, color: (int, int, int)):
        pass


class TextInputProtocol(UIElement, Protocol):
    color: (int, int, int, int)
    model: Any
    model_attribute: str
    font_size: int
    font_name: str
    length: int
    document: pyglet.text.document.UnformattedDocument
    layout: pyglet.text.layout.IncrementalTextLayout
    caret: AbstractDynamicCaret

    @property
    def active(self) -> bool:
        pass

    @active.setter
    def active(self, new_value: bool):
        pass

    def text_changed(self):
        pass


class ViewModel(Protocol):

    def request_update(self):
        pass

    def need_redraw(self) -> bool:
        pass


class View(Protocol):
    batch: pyglet.graphics.Batch
    window: pyglet.window.Window

    @property
    def focus(self) -> Optional[TextInputProtocol]:
        pass

    def content(self) -> UIElement:
        pass

    def click(self, x, y, button, modifiers):
        pass

    def draw(self, x=None, y=None, w=None, h=None, batch=None):
        pass

    def layout(self):
        pass

    def register_model(self, model: ViewModel):
        pass

    def remove_model(self, model: ViewModel):
        pass

    def on_resize(self, width, height):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_text(self, text):
        pass

    def on_text_motion(self, motion):
        pass

    def on_text_motion_select(self, motion):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass
