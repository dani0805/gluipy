import math
from typing import Protocol, Any, Collection, Optional

from gluipy.interface import UIElement, ViewModel
from gluipy.container import VContainer
from gluipy.layout import Space
from gluipy.modifier import Border


class TableCell(UIElement, Protocol):
    model: Any
    index: int

    def __init__(self, model: Any, index: int):
        pass

class TableDelegate(Protocol):

    def current_item(self) -> int:
        pass

class TableModel(ViewModel, Collection, Protocol):

    def model_state(self) -> str:
        pass

    def get_scroll(self) -> Optional[int]:
        pass

    def invalidate_scroll(self):
        pass

    def set_table_delegate(self, table:TableDelegate):
        pass


class Table(Border, TableDelegate):
    offsets: {str: int} = {}
    cell_cache: {str: {int: TableCell}} = {}
    v_hugging_force = 200
    v_compression_resistance = 200
    h_hugging_force = 400
    h_compression_resistance = 400

    def __init__(self, cell_class: type(TableCell), model: TableModel, table_id: str):
        self.cache_id = table_id
        self.cell_class = cell_class
        self.model = model
        self.model.set_table_delegate(self)
        self.num_elems = len(model)
        if self.num_elems > 0:
            sample_model = model[0]
            sample_cell = cell_class(sample_model, 0)
            _, self.cell_height = sample_cell.size_requested()
        else:
            sample_cell = Space()

        self.offset = Table.offsets.get(table_id, 0)
        self.table_id = table_id
        Table.cell_cache[table_id] = {0: sample_cell}
        super(Table, self).__init__(VContainer([sample_cell, Space()], f"{self.cache_id}-container"), thickness=0, radius=0, color=(255, 255, 255))

    def _state_hash(self) -> Optional[str]:
        state_dict = super(Table, self)._state_hash() + f"|{self.model.model_state()}|{self.offset}"
        return state_dict

    def draw(self, x: int, y: int, w: int, h: int, batch, cached=True) -> bool:
        return super(Table, self).draw(x, y, w, h, batch, cached=cached)

    def draw_content(self, x, y, w, h, batch):
        if self.num_elems > 0:
            eff_height = self.cell_height
            model_index = self.model.get_scroll()
            if model_index is not None:
                self.offset = (eff_height + 8) * model_index
            eff_offset = self.offset
            #print(eff_offset, self.offset)
            first_element = min(math.floor((eff_offset + 8) / (eff_height + 8)), self.num_elems)
            last_element = min(math.ceil((eff_offset + h + 8) / (eff_height + 8)), self.num_elems)
            content_h = (eff_height + 8) * (last_element - first_element) - 8
            content_y = y + h + eff_offset - last_element * (eff_height + 8)
            #print(content_y, content_h)
            elements = []
            for i in range(first_element, last_element):
                if i in Table.cell_cache[self.table_id]:
                    elements.append(Table.cell_cache[self.table_id][i])
                else:
                    elements.append(self.cell_class(self.model[i], i))

            content = VContainer(elements + [Space()], f"{self.cache_id}-container")
            content.size_requested()
            content.draw(x, content_y, w, content_h, batch, True)
        else:
            Space().draw(x, y, w, h, batch)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._x < x < self._x + self._w and self._y < y < self._y + self._h:
            self.offset += scroll_y * 8
            self.offset = max(self.offset, 0)
            self.offset = min(self.offset, self.num_elems * self.cell_height / 2)
            Table.offsets[self.table_id] = self.offset
            self.model.invalidate_scroll()
            self.model.request_update()

    def current_item(self):
        return min(math.floor((self.offset + 8) / (self.cell_height + 8)), self.num_elems)



