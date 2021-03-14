from typing import Any, Generic, TypeVar

LEFT = TypeVar("LEFT")
RIGHT = TypeVar("RIGHT")


class AttrMapMeta(type):
    def __getattr__(cls, name):
        return AttrPath(name)

    def __getitem__(cls, name_or_index):
        return AttrPath((name_or_index,))

    def __call__(cls):
        return AttrPath(None)


class AttrMap(metaclass=AttrMapMeta):
    pass


class AttrPath:
    def __init__(self, name) -> None:
        self.__path__ = []
        self.__path__.append(name)

    def __getattr__(self, name):
        self.__path__.append(name)
        return self

    def __getitem__(self, name):
        self.__path__.append((name,))
        return self

    def __call__(self) -> Any:
        self.__path__.append(None)
        return self

    def __str__(self):
        s = AttrMap.__name__
        for x in self.__path__:
            if isinstance(x, tuple):
                s += f"[{x[0]!r}]"
            elif isinstance(x, str):
                s += f".{x}"
            elif x is None:
                s += "()"

        return s

    def __repr__(self) -> str:
        return str(self)


class Accesor:
    def __init__(self, attrpath: AttrPath) -> None:
        self.attrpath = attrpath

    def __str__(self) -> str:
        return str(self.attrpath)

    def __repr__(self) -> str:
        return repr(self.attrpath)


class MappingMeta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        map_attrs = {k: v for k, v in attrs.items() if isinstance(v, AttrPath)}

        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        cls.__fields__ = {k: Accesor(v) for k, v in map_attrs.items()}
        for k, v in cls.__fields__.items():
            setattr(cls, k, v)

        return cls

    def __str__(self) -> str:
        return f"Mapper({self.__fields__!r})"  # type: ignore


class Mapper(Generic[LEFT, RIGHT], metaclass=MappingMeta):
    def pull(self, from_: RIGHT, to: LEFT) -> LEFT:
        return to

    def push(self, from_: LEFT, to: RIGHT) -> RIGHT:
        return to


def test_attr_map():
    field = AttrMap.obj.data["persons"][0].name
    assert str(field) == "AttrMap.obj.data['persons'][0].name"


def test_mapper():
    class ObjMapper(Mapper[LEFT, RIGHT]):
        name = AttrMap.obj.data["persons"][0].name

        @property
        def item(self):
            return 1

        @staticmethod
        def item2(self):
            return 1

    assert [x for x in ObjMapper.__fields__.keys()] == ["name"]

    """このクラスは何をするものですか。
    ETLなどであるオブジェクトの属性を、あるオブジェクトの属性に取り込みたい。
    そのような場合、単にスクリプトを書くのではなく、設定ライクな取り込みができればうれしい。
    """
