from typing import Protocol, Optional
import pyglet
from pyglet import gl, image, sprite

from gluipy.cache import Cache
from gluipy.interface import UIElement, View, TextInputProtocol, ViewModel


class ModifierMeta(type):
    modifiers = {}

    def __init__(cls, clsname, bases, methods):
        super().__init__(clsname, bases, methods)
        ModifierMeta.modifiers[cls.__name__.lower()] = cls


class ModifierProtocolMeta(ModifierMeta, type(Protocol)):
    pass


def camel_to_snake(name):
    return ''.join(word for word in name.split('_'))


class BaseUIElement(UIElement):
    caching = True
    h_compression_resistance = 750
    h_hugging_force = 750
    v_compression_resistance = 750
    v_hugging_force = 750
    _x = None
    _y = None
    _w = None
    _h = None
    background_color = None
    background_opacity = 255
    cache_id = None

    def _state_hash(self) -> Optional[str]:
        return None

    def request_redraw(self):
        self._x, self._y, self._w, self._h = None, None, None, None

    def __getattr__(self, item):
        item_name = ''.join(word for word in item.split('_'))
        if item_name in ModifierMeta.modifiers:
            cls = ModifierMeta.modifiers[item_name]

            def func(*args, **kwargs):
                return cls(self, *args, **kwargs)

            return func
        raise AttributeError(f"no attribute {item} found")

    def draw_cached(self, x: int, y: int, w: int, h: int, batch: pyglet.graphics.Batch) -> bool:
        object_hash, state_hash = self.cache_id, self._state_hash()
        if object_hash is not None and state_hash is not None:
            cached_element = Cache.get_cached_uielement(object_hash, state_hash)
            if cached_element is not None:
                return cached_element.draw(x, y, w, h, batch)
        return False

    def draw(self, x: int, y: int, w: int, h: int, batch: pyglet.graphics.Batch, cached=True) -> bool:

        caching_now = self.cache_id and self.caching and cached
        if caching_now:
            was_cached = self.draw_cached(x, y, w, h, batch)
            if was_cached:
                self._x, self._y, self._w, self._h = x, y, w, h
                return True
        draw_batch = pyglet.graphics.Batch() if caching_now else batch
        self.draw_content(x, y, w, h, draw_batch)
        self._x, self._y, self._w, self._h = x, y, w, h
        if caching_now:
            draw_batch.draw()
            object_hash, state_hash = self.cache_id, self._state_hash()
            buffer = image.get_buffer_manager().get_color_buffer()
            if 0 <= x and x + w <= buffer.width and 0 <= y and y + h <= buffer.height:
                try:
                    sprt = sprite.Sprite(img=buffer.get_region(x, y, w, h).get_texture())
                    Cache.save_cache(object_hash, state_hash, x, y, w, h, sprt)
                except:
                    pass
        return False

    def click(self, x, y, button, modifiers, view):
        if self._x is None or (self._x < x < self._x + self._w and self._y < y < self._y + self._h):
            if hasattr(self, "_click"):
                self._click(view)
                return True
        return False

    def on_mouse_motion(self, x, y, dx, dy):
        pass


class BaseView(View):
    root: Optional[UIElement]

    def __init__(self, window: pyglet.window.Window = None):
        self.redraw = False
        self.batch = pyglet.graphics.Batch()
        self.window = window
        pyglet.gl.glScalef(0.5, 0.5, 0.5)
        self._focus: Optional[TextInputProtocol] = None
        self._models: [ViewModel] = []
        self.root = None
        self.focus_x = None
        self.focus_y = None

        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            self.on_mouse_scroll(x * 2, y * 2, scroll_x * 2, scroll_y * 2)

        window.event(on_mouse_scroll)

        def on_mouse_motion(x, y, dx, dy):
            self.on_mouse_motion(x * 2, y * 2, dx * 2, dy * 2)

        window.event(on_mouse_motion)

        def on_mouse_press(x, y, button, modifiers):
            self.click(x * 2, y * 2, button, modifiers)

        window.event(on_mouse_press)

        def on_text(text):
            self.on_text(text)

        window.event(on_text)

        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            self.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

        window.event(on_mouse_drag)

        def on_text_motion(motion):
            self.on_text_motion(motion)

        window.event(on_text_motion)

        def on_text_motion_select(motion):
            self.on_text_motion_select(motion)

        window.event(on_text_motion_select)

        def on_draw():
            self.draw()

        window.event(on_draw)

        def on_resize(width, height):
            self.on_resize(width, height)

        window.event(on_resize)

    @property
    def focus(self) -> Optional[TextInputProtocol]:
        return self._focus

    @focus.setter
    def focus(self, new_value: Optional[TextInputProtocol]):
        if self._focus is not None:
            self._focus.active = False
        self._focus = new_value

    def register_model(self, model: ViewModel):
        self._models.append(model)

    def remove_model(self, model: ViewModel):
        self._models.remove(model)

    def draw(self, x=None, y=None, w=None, h=None, batch=None):
        if self.window is not None:
            self.window.clear()
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            backdrop = pyglet.shapes.Rectangle(0, 0, self.window.width * 2, self.window.height * 2, (230, 230, 230))
            backdrop.draw()

        self.layout()
        own_batch = batch is None
        if not own_batch:
            self.batch = batch

        self.root.draw(x if x else 0, y if y else 0, w if w else self.window.width * 2,
                       h if h else self.window.height * 2, self.batch)
        if own_batch:
            self.batch.draw()

    def layout(self):
        if self.root is None:
            self.redraw = True
        if not self.redraw:
            for m in self._models:
                self.redraw = m.need_redraw()
                if self.redraw:
                    break
        if self.redraw:
            self.redraw = False
            self.root = self.content()
            self.root.size_requested()

    def on_resize(self, width, height):
        self.redraw = True

    def click(self, x, y, button, modifiers):
        self.focus = None
        self.root.click(x, y, button, modifiers, self)

        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)
            self.focus.text_changed()

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)
            self.focus.text_changed()

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

    def on_mouse_motion(self, x, y, dx, dy):
        self.root.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.root.on_mouse_scroll(x, y, scroll_x, scroll_y)
