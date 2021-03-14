from pydantic import BaseModel
from typing import Callable, Dict
from functools import partial

class Repoisotry(BaseModel):
    name: str = "default"
    key_selector: Callable = partial(lambda x: x) # WARNING: https://github.com/samuelcolvin/pydantic/issues/1596 defualt値の有無で挙動が変わってしまう
    dic: Dict = {}
    #__slots__ = ["dic"]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.dic = {}

    def select_key(self, obj):
        selector = self.key_selector
        return selector(obj)

    def exists_by_key(self, key):
        return True if key in self.dic else False

    def append(self, obj):
        if obj is None:
            raise ValueError("obj[{}] is none.".format(obj))

        key = self.select_key(obj)
        if key is None:
            raise ValueError("key[{}] is none.".format(key))
        
        if key in self.dic:
            raise ValueError("duplicate key: {}".format(key))

        self.dic[key] = obj

        return obj

    def update(self, obj):
        if obj is None:
            raise ValueError("obj[{}] is none.".format(obj))

        key = self.key_selector(obj)

        if key is None:
            raise ValueError("key[{}] is none.".format(key))

        self.dic[key] = obj
        return obj

    def get(self, key):
        if key is None:
            raise ValueError("key[{}] is none.".format(key))
        
        obj = self.dic.get(key)
        return obj

    def list(self):
        for key, value in self.dic.items():
            yield key, value

