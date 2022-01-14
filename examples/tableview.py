import pyglet

from gluipy.base import BaseView
from gluipy.interface import UIElement
from gluipy.button import Button
from gluipy.container import VContainer, HContainer
from gluipy.layout import Space
from gluipy.table import Table, TableCell
from gluipy.text import Label, TextInput

# needed to initialize the modifiers registry, do not remove import!
import gluipy.modifier

from peopledb import Person, Model


class Cell(VContainer, TableCell):

    def __init__(self, model: Person, index: int):
        self.person = model
        self.cache_id = f"cell|{index}"
        super(Cell, self).__init__([
            HContainer([
                VContainer([
                    HContainer(
                        [Label(f"{self.person.last_name}, {self.person.first_name}", cache_id=f"name|{index}", font_size=24, color=(20, 30, 80, 255)),
                         Space()], f"name_row|{index}"),
                    HContainer([Label(self.person.address, cache_id=f"address|{index}", font_size=20, color=(20, 30, 80, 255)), Space()], f"add_row1|{index}"),
                    HContainer([Label(f"{self.person.city}, {self.person.zip} {self.person.state}", cache_id=f"address2|{index}", font_size=20,
                                      color=(20, 30, 80, 255)), Space()], f"add_row2|{index}")
                ], cache_id=f"left_col|{index}", gutter=0),
                Space(),
                VContainer([
                    HContainer([Space(), Label(self.person.email, cache_id=f"email|{index}", font_size=20, color=(20, 30, 80, 255))], f"email_row|{index}"),
                    HContainer([Space(), Label(self.person.phone1, cache_id=f"phone1|{index}", font_size=20, color=(20, 30, 80, 255))], f"phone_row1|{index}"),
                    HContainer([Space(), Label(self.person.phone2, cache_id=f"phone2|{index}", font_size=20, color=(20, 30, 80, 255))], f"phone_row2|{index}")
                ], cache_id=f"right_col|{index}", gutter=0 )
            ], cache_id=f"cell_body|{index}")
                .background((210, 220, 220) if index % 2 == 0 else (240, 240, 240))
                .padding((10, 0, 10, 0))
        ], cache_id=f"cell_box|{index}")


mymodel = Model("us-500.csv")


class MyView(BaseView):
    def content(self) -> UIElement:
        return VContainer([
            HContainer([
                *[
                    Button(f"- {-i}", cache_id=f"scroll-{-i}", font_size=24, radius=10).on_click(mymodel.scroll(i))
                    for i in range(- 10 if mymodel.current_index() > 9 else -1 if mymodel.current_index() > 0 else 0, 0, 9)
                ],
                HContainer([
                    Label("search: ", cache_id=f"search-label", font_size=24, padding=(10, 3, 10, 3)),
                    TextInput(font_size=24, model=mymodel, model_attribute="search", length=15, cache_id="search").padding((10, 0, 10, 21))
                ], "searchbox").background((250, 250, 250)).border(radius=0, thickness=2),
                *[
                    Button(f"+ {i}", cache_id=f"scroll+{i}", font_size=24, radius=10).on_click(mymodel.scroll(i))
                    for i in range(1, min(10 + 3, len(mymodel.data)- mymodel.current_index()), 9)
                ],
                Button("↻", cache_id=f"reset", font_size=36, radius=10).on_click(mymodel.reset())
            ], cache_id="toolbar").padding((10, 0, 10, 10)),
            Table(Cell, mymodel, "user_cell")
        ], cache_id="body")


config = pyglet.gl.Config(double_buffer=True, stencil_size=8)
window = pyglet.window.Window(config=config, width=800, height=600, resizable=True)
view = MyView(window)
view.register_model(mymodel)

pyglet.app.run()
