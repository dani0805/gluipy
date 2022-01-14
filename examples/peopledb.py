import csv
from abc import ABC
from typing import Any, Iterator, Optional

from gluipy.interface import ViewModel
from gluipy.table import TableModel, TableDelegate


class Person:
    first_name: str
    last_name: str
    company_name: str
    address: str
    city: str
    county: str
    state: str
    zip: int
    phone1: str
    phone2: str
    email: str
    web: str

    def __init__(self, *,
                 first_name: str,
                 last_name: str,
                 company_name: str,
                 address: str,
                 city: str,
                 county: str,
                 state: str,
                 zip: int,
                 phone1: str,
                 phone2: str,
                 email: str,
                 web: str):
        self.first_name = first_name
        self.last_name = last_name
        self.company_name = company_name
        self.address = address
        self.city = city
        self.county = county
        self.state = state
        self.zip = zip
        self.phone1 = phone1
        self.phone2 = phone2
        self.email = email
        self.web = web


class Model(TableModel):

    _search: str
    _data: [Any]
    _redraw = False

    def __init__(self, filepath):
        self.table_delegate = None
        self.filepath = filepath
        self.search = None
        self.index = 0

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self) -> Iterator[Any]:
        for e in self._data:
            yield e

    def __contains__(self, __x: object) -> bool:
        return __x in self._data

    @property
    def data(self):
        if self._data is None:
            self.load_data()
        return self._data

    @property
    def search(self):
        return self._search

    @search.setter
    def search(self, new_value):
        self._search = new_value
        self.load_data()

    def scroll(self, increment):
        def wrapped(element):
            if self.index is None:
                self.index = self.table_delegate.current_item()
            self.index += increment
            self.index = min(max(self.index, 0), len(self._data))
            self._redraw = True

        return wrapped

    def reset(self):
        def wrapped(element):
            self.index = 0
            self._redraw = True

        return wrapped

    def load_data(self):
        self._data = []
        with open(self.filepath, newline='') as csvfile:
            users = csv.reader(csvfile, delimiter=',', quotechar='"')
            first = True
            for row in users:
                if first:
                    first = False
                    continue
                if self._search is not None and self._search != "":
                    match = False
                    for attr in (0,1,3,4,6,7,8,9,10):
                        if self._search in row[attr]:
                            match = True
                            break
                    if not match:
                        continue
                self._data.append(Person(
                    first_name=row[0],
                    last_name=row[1],
                    company_name=row[2],
                    address=row[3],
                    city=row[4],
                    county=row[5],
                    state=row[6],
                    zip=int(row[7]),
                    phone1=row[8],
                    phone2=row[9],
                    email=row[10],
                    web=row[11])
                )
        self.index = 0
        self._redraw = True

    def need_redraw(self) -> bool:
        if self._redraw:
            self._redraw = False
            return True
        return False

    def request_update(self):
        self._redraw = True

    def model_state(self) -> str:
        return f"{self._search}|{self.index}"

    def invalidate_scroll(self):
        self.index = None

    def set_table_delegate(self, table:TableDelegate):
        self.table_delegate = table

    def current_index(self):
        if self.index is not None:
            return self.index
        if self.table_delegate is not None:
            return self.table_delegate.current_item()

        return 0

    def get_scroll(self) -> Optional[int]:
        return self.index
