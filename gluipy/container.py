from functools import reduce
from typing import Optional

from pyglet import gl

from gluipy.base import BaseUIElement
from gluipy.interface import UIElement, Container


class BaseContainer(Container, BaseUIElement):
    H = "w"
    V = "h"
    direction: str = H
    __desired_size: (int, int)

    def __init__(self, elements: [UIElement], cache_id=None, gutter=8):
        self.cache_id = cache_id
        self.elements = elements
        if self.direction == BaseContainer.V:
            self.elements = list(reversed(self.elements))

        for el in elements:
            el.container = self
            if hasattr(el, "pre_layout"):
                el.pre_layout(self.direction)
        self.gutter = gutter

    def pre_layout(self, direction):
        if direction == self.direction == BaseContainer.H:
            self.h_compression_resistance = min(map(lambda x: x.h_compression_resistance, self.elements))
            self.h_hugging_force = min(map(lambda x: x.h_hugging_force, self.elements))
        if direction == self.direction == BaseContainer.V:
            self.v_compression_resistance = min(map(lambda x: x.v_compression_resistance, self.elements))
            self.v_hugging_force = min(map(lambda x: x.v_hugging_force, self.elements))

    def _object_hash(self) -> Optional[dict]:
        hash_dict = {"w": self._w, "h": self._h}
        for i, e in enumerate(self.elements):
            e_hash = e._object_hash()
            if e_hash is not None:
                hash_dict.update({f"e_{i}": e._object_hash()})
        return hash_dict

    def _state_hash(self) -> Optional[str]:
        state_dict = "|".join([e._state_hash() for e in self.elements])
        return state_dict

    def draw_content(self, x, y, w, h, batch):
        # if direction allocated space is less then requested
        dir_attr = "_w" if self.direction == BaseContainer.H else "_h"
        allocated_space = w if self.direction == BaseContainer.H else h
        desired_space = getattr(self, dir_attr)
        temp_space = desired_space
        # if direction allocated space is less then requested
        cr_attr = "h_compression_resistance" if self.direction == BaseContainer.H else "v_compression_resistance"
        if temp_space > allocated_space:
            # sort elements by compression resistance
            sorted_els = sorted(self.elements, key=lambda elem: getattr(elem, cr_attr))
            # until we fit into the allocated space
            index = 0
            while temp_space > allocated_space:
                # take the first entries
                to_update = []
                if index >= len(sorted_els):
                    # we are giving up
                    break
                compression_resistance = getattr(sorted_els[index], cr_attr)
                for el in sorted_els[index:]:
                    if getattr(el, cr_attr) > compression_resistance:
                        break
                    to_update.append(el)
                    index += 1
                space_diff = temp_space - allocated_space
                # set their direction size so that it fits the required space, possibly 0
                selected_el_space = reduce(lambda a, b: a+b, list(map(lambda elem: getattr(elem, dir_attr), to_update)))
                if space_diff > selected_el_space:
                    # set to 0 and continue
                    for elem in to_update:
                        temp_space -= getattr(elem, dir_attr)
                        setattr(elem, dir_attr, 0)
                else:
                    temp_space = self.resize_proportionally(allocated_space, dir_attr, temp_space, to_update)
        # if direction allocated space is more then requested
        if temp_space < allocated_space:
            hf_attr = "h_hugging_force" if self.direction == BaseContainer.H else "v_hugging_force"
            # sort elements by hugging force
            sorted_els = sorted(self.elements, key=lambda elem: getattr(elem, hf_attr))
            # take the first entries
            to_update = []

            hugging_force = getattr(sorted_els[0], hf_attr)
            for el in sorted_els:
                if getattr(el, hf_attr) > hugging_force:
                    break
                to_update.append(el)
            # set their direction size so that it fills the allocated space
            temp_space = self.resize_proportionally(allocated_space, dir_attr, temp_space, to_update)

        # once all the children comply with allocated space update own space allocation
        setattr(self, dir_attr, allocated_space)

        # loop through elements and allocated the other direction
        other_attr = "_h" if self.direction == BaseContainer.H else "_w"
        other_allocated_space = h if self.direction == BaseContainer.H else w
        # update own space allocation, and use it later to draw children
        setattr(self, other_attr, other_allocated_space)

        # loop through elements and draw them with their allocated space
        current_x = x
        current_y = y
        cached = len(self.elements) > 1
        for elem in self.elements:
            this_w = elem._w if self.direction == BaseContainer.H else self._w
            this_h = elem._h if self.direction == BaseContainer.V else self._h
            elem.draw(current_x, current_y, this_w, this_h, batch, cached=cached)
            if self.direction == BaseContainer.H:
                current_x += elem._w + self.gutter
            else:
                current_y += elem._h + self.gutter
        self._x, self._y, self._w, self._h = x, y, w, h

    def resize_proportionally(self, allocated_space, dir_attr, desired_space, elements):
        space_diff = desired_space - allocated_space
        selected_el_space = reduce(lambda a, b: a+b, map(lambda elem: getattr(elem, dir_attr), elements))
        if selected_el_space == 0:
            return allocated_space
        for elem in elements:
            proportional_space = int(space_diff * getattr(elem, dir_attr) / selected_el_space)
            desired_space -= proportional_space
            setattr(elem, dir_attr, getattr(elem, dir_attr) - proportional_space)
        # correct rounding errors
        if desired_space != allocated_space:
            rounding_diff = (desired_space - allocated_space)
            desired_space -= rounding_diff
            setattr(elements[0], dir_attr, getattr(elements[0], dir_attr) - rounding_diff)
        return desired_space

    def size_requested(self) -> (int, int):
        if self._w is None or self._h is None:
            def size_add(e1: (int, int), e2: (int, int)) -> (int, int):
                if self.direction == BaseContainer.H:
                    return e1[0] + e2[0] + self.gutter, max(e1[1], e2[1])
                elif self.direction == BaseContainer.V:
                    return max(e1[0], e2[0]), e1[1] + e2[1] + self.gutter
                else:
                    raise ValueError(f"invalid direction, must be BaseContainer.H or BaseContainer.V: {self.direction}")

            self._w, self._h = reduce(size_add, map(lambda x: x.size_requested(), self.elements))
        return self._w, self._h

    def click(self, x, y, button, modifiers, view):
        if super(BaseContainer, self).click(x, y, button, modifiers, view):
            return True
        if self._x is None or (self._x < x < self._x + self._w and self._y < y < self._y + self._h):
            for el in self.elements:
                found = el.click(x, y, button, modifiers, view)
                if found:
                    return True
        return False

    def on_mouse_motion(self, x, y, dx, dy):
        for e in self.elements:
            e.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for e in self.elements:
            e.on_mouse_scroll(x, y, scroll_x, scroll_y)



class VContainer(BaseContainer):
    direction = BaseContainer.V
    h_compression_resistance = 750
    h_hugging_force = 750
    v_compression_resistance = 700
    v_hugging_force = 700


class HContainer(BaseContainer):
    direction = BaseContainer.H
    h_compression_resistance = 700
    h_hugging_force = 700
    v_compression_resistance = 750
    v_hugging_force = 750
