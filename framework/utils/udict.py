import inspect
from typing import Any, Dict

undefined = inspect._empty  # type: ignore


class UndefinedDict(dict):
    """undefinedな値は無視する特殊な辞書。"""

    undefined: inspect._empty = undefined  # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        removes = [k for k, v in self.items() if v is undefined]
        for k in removes:
            del self[k]

    def update(self, *args, **kwargs):
        raise NotImplementedError()

    def setdefault(self, *args, **kwargs):
        raise NotImplementedError()

    def fetch_attr(self, obj, name: str, default=undefined):
        val = getattr(obj, name, default)
        self.__setitem__(name, val)
        return val

    def fetch_item(self, obj, key, default=undefined):
        val = obj.get(key, default)
        self.__setitem__(key, val)
        return val

    def fetch_index(self, obj, index, default=undefined):
        try:
            val = obj[index]
        except IndexError:
            val = default
        except:
            raise
        self.__setitem__(index, val)
        return val

    def __setitem__(self, name: str, value) -> None:
        if value is undefined:
            pass
        else:
            return super().__setitem__(name, value)


class MappingDict(UndefinedDict):
    allow_extra = False
    from_to: Dict[Any, Any] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        keys = [x for x in self]
        for key in keys:
            self[key] = self.pop(key)

    def __setitem__(self, name: str, value) -> None:
        if value is undefined:
            return
        exist = name in self.__class__.from_to
        if exist:
            to = self.__class__.from_to[name]
            return super().__setitem__(to, value)
        elif self.__class__.allow_extra:
            return super().__setitem__(name, value)
        else:
            raise KeyError(name)
