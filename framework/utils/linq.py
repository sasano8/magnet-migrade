from __future__ import annotations

import asyncio
import functools
import inspect
import itertools
import operator
from typing import (
    Any,
    Callable,
    Coroutine,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    NoReturn,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    cast,
)

import pandas as pd
from pydantic import BaseModel, parse_obj_as
from pydantic.tools import NameFactory


class Undefined:
    pass


undefined = Undefined()

T = TypeVar("T")
R = TypeVar("R")
_T_co = TypeVar("_T_co", covariant=True)
_O_co = TypeVar("_O_co", covariant=True)


class GeneratorFunctionWrapper:
    def __init__(self, func) -> None:
        self.func = func

    def __iter__(self):
        return self.func()


def convert_to_queryable(self):
    if isinstance(self, Linq):
        return self

    result: Any = None

    if isinstance(self, dict):
        result = self.items()
    elif isinstance(self, Iterator):
        result = self
    elif isinstance(self, Iterable):
        result = self
    elif hasattr(self, "__getitem__"):  # __getitem__はiterableであるが、isinstanceで判定不可
        result = self
    elif inspect.isgeneratorfunction(self):
        result = GeneratorFunctionWrapper(self)
    else:
        return None

    return LinqRoot(result)


class Linq(Iterable[T]):
    # class Linq(Iterable[T], Generic[T]):
    __root__: Iterable[T]

    def __init__(self, __root__: Iterable[T], func: Callable = iter):
        self.__root__ = convert_to_queryable(__root__)
        self.generator_function = func

        if self.__root__ is None:
            raise ValueError(f"Not iterable: {type(__root__)} {__root__}")

    def __iter__(self) -> Iterator[T]:
        return self.generator_function(self.__root__)

    def __str__(self) -> str:
        return list(self).__str__()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}({list(self).__repr__()})"

    # dont implement.
    # def __len__(self):
    # 詳細は　test_python_spec_len　を参照

    @property
    def _get_type(self) -> Literal["", "root", "dummy"]:
        return ""

    def __call__(self, iterable: Iterable[T]) -> Linq[T]:
        """クエリをイテレータにアタッチし、新しいLinqオブジェクトを作成する。"""
        chains = self._get_chains()

        if not chains[0]._is_dummy():
            raise Exception("ルートはdummyでなければいけません。")

        del chains[0]
        latest = Linq(iterable)

        for chain in chains:
            query = chain.__root__
            func = query.func
            args = query.copy_args(latest)
            new_query = Linq(functools.partial(func, *args))
            latest = Linq(new_query)

        return latest

    # def _get_root_type(self):
    #     # not root
    #     if isinstance(self.__root__, Linq):
    #         return -1

    #     if self.__root__:
    #         return 1  # iterable root
    #     else:
    #         return 0  # empty root

    # def _is_dummy(self):
    #     result = self._get_root_type()
    #     if result == 0:
    #         return True
    #     else:
    #         return False

    # def _is_root(self):
    #     result = self._get_root_type()
    #     if result == -1:
    #         return False
    #     else:
    #         return True

    # def _get_query(self):
    #     iter = self.__root__
    #     if hasattr(iter, "self_index"):
    #         self_index = iter.self_index
    #         return iter

    #     else:
    #         return None

    # def _get_chains(self):
    #     chaines = [self]
    #     is_root = self._is_root()

    #     while not is_root:
    #         chain: Any = self.__root__
    #         chaines.append(chain)
    #         is_root = chain._is_root()

    #     chaines = list(reversed(chaines))
    #     return chaines

    # @linq
    # def _items(self) -> "Linq":
    #     def evalute(iterator):
    #         yield from iterator.__root__.items()

    #     partial = functools.partial(evalute, self)
    #     return Query(partial, 0)

    # ここを実装すると`to_dict => dict(self)`の挙動が変わるので注意
    # def keys(self: Iterable[T]):
    #     raise NotImplementedError()

    # def values(self: Iterable[T]):
    #     raise NotImplementedError()

    # def items(self: Iterable[T]):
    #     raise NotImplementedError()

    def filter(self: Iterable[T], *funcs: Callable[[T], bool]) -> Linq[T]:
        return Linq.filter_and(self, *funcs)

    def filter_and(self: Iterable[T], *funcs: Callable[[T], bool]) -> Linq[T]:
        def is_all_true(target):
            for func in funcs:
                if not func(target):
                    return False
            return True

        def evalute(iterable):
            for item in iterable:
                if is_all_true(item):
                    yield item

        return Linq(self, evalute)

    def filter_or(self, *funcs: Callable[[T], bool]) -> Linq[T]:
        def is_hit(target):
            for func in funcs:
                if func(target):
                    return True
            return False

        def evalute(iterable):
            for item in iterable:
                if is_hit(item):
                    yield item

        return Linq(self, evalute)

    def filter_not(self, *funcs: Callable[[T], bool]) -> Linq[T]:
        raise NotImplementedError()

    def filter_in(self, selector, *arr):
        def evalute(iterable):
            for item in iterable:
                if item in arr:
                    yield item

        return Linq(self, evalute)

    def filter_not_in(self, arr, selector):
        def evalute(iterable):
            for item in iterable:
                if not item in arr:
                    yield item

        return Linq(self, evalute)

    def filter_between(self, arr):
        raise NotImplementedError()

    def filter_not_between(self, arr):
        raise NotImplementedError()

    def filter_with_enumerate(self, func: Callable[[int, T], bool]) -> Linq[T]:
        def evaluate(iterable):
            for index, item in enumerate(iterable):
                if func(index, item):
                    yield item

        return Linq(self, evaluate)

    def filter_with_enumerate_not(self, func: Callable[[int, T], bool]) -> Linq[T]:
        def evaluate(iterable):
            for index, item in enumerate(iterable):
                if not func(index, item):
                    yield item

        return Linq(self, evaluate)

    def filter_isinstance(self, type_: Type[T]) -> Linq[T]:
        type_ = None.__class__ if type_ is None else type_
        return self.filter(lambda x: isinstance(x, type_))

    def filter_isinstance_not(self, type_: Type[T]) -> Linq[T]:
        type_ = None.__class__ if type_ is None else type_
        return self.filter_not(lambda x: isinstance(x, type_))

    def filter_even(self) -> "Linq":
        return self.filter(lambda x: x % 2 == 0)

    def filter_odd(self) -> "Linq":
        return self.filter(lambda x: x % 2 != 0)

    def distinct(self, selector=lambda x: x, do_raise: bool = False) -> Linq[T]:
        if do_raise:
            raise NotImplementedError()

        def evalute(iterable):
            exists = set()
            for item in iterable:
                if item in exists:
                    continue
                exists.add(selector(item))
                yield item

        return Linq(self, evalute)

    def take(self, count) -> Linq:
        def evaluate(iterable):
            counter = 0
            for index, item in enumerate(iterable):
                if counter < count:
                    yield item
                else:
                    break
                counter += 1

        return Linq(self, evaluate)

    def skip(self, count) -> Linq:
        def evaluate(iterable):
            counter = 0
            it = iterable.__iter__()

            try:
                while counter < count:
                    next(it)
                    counter += 1

                while True:
                    yield next(it)

            except StopIteration as e:
                pass

            except Exception as e:
                raise

        return Linq(self, evaluate)

    def buffer(self, size: int) -> Linq:
        """返す最大の配列数を制限する　リスト化した後に取ればいいからいらないかも"""
        raise NotImplementedError()

    def take_while(self, func) -> Linq:
        def evaluate(iterable):
            yield from itertools.takewhile(func, iterable)

        return Linq(self, evaluate)

    def drop_while(self, func) -> Linq:
        def evaluate(iterable):
            yield from itertools.dropwhile(func, iterable)

        return Linq(self, evaluate)

    def step(self, step: int = 1) -> Linq:
        if step <= 0:
            raise Exception("stepは1以上を指定してください。")

        def evaluate(iterable):
            count = step
            for item in iterable:
                if count % step == 0:
                    yield item
                count += 1

        return Linq(self, evaluate)

    def split(self):
        raise NotImplementedError()

    def slice(self, start: int = 0, stop: int = None, step: int = 1) -> Linq:
        def evaluate(iterable):
            yield from itertools.islice(iterable, start, stop, step)

        return Linq(self, evaluate)

    def map(self: Iterable[T], func: Callable[[T], R]) -> Linq[R]:
        def evalute(iterable):
            yield from map(func, iterable)

        return Linq(self, evalute)  # type: ignore

    def select(self: Iterable[T], func: Callable[[T], R]) -> Linq[R]:
        return Linq.map(self, func)

    def map_enumerate(self, func: Callable[[int, T], R]) -> Linq[R]:
        raise NotImplementedError()

    def parse(self, type_: Type[R], type_name: Optional[NameFactory] = None) -> Linq[R]:
        """要素を指定した型に解釈します。解釈は、pydanticのparse_obj_asを利用します。"""
        mapper = lambda x: parse_obj_as(type_, x, type_name=type_name)
        return Linq.map(self, mapper)

    def regex(self) -> Linq:
        raise NotImplementedError()

    def flatten(self) -> Linq:
        raise NotImplementedError()

    def fill(self, default=0) -> Linq[T]:
        mapper = lambda x: default if x is None else x
        return Linq.map(self, mapper)

    def pivot(self, default=None):
        raise NotImplementedError()

    def zip(self, iterable) -> Linq[T]:
        return Linq.zip_shortest(self, iterable)

    def zip_shortest(self, iterable) -> Linq:
        def evaluate(self):
            yield from zip(self, iterable)

        return Linq(self, evaluate)

    def zip_longest(self, *iterable, fillvalue=None) -> Linq:
        def evaluate(self):
            yield from itertools.zip_longest(self, *iterable, fillvalue=fillvalue)

        return Linq(self, evaluate)

    def cast(self, type_: Type[R]) -> Linq[R]:
        raise NotImplementedError()

    def chain(self, *iterables: Iterable[T]) -> Linq[T]:
        """compatible itertools.chain"""

        def evalute(iterable):
            yield from itertools.chain(iterable, *iterables)

        return Linq(self, evalute)

    def select_many(self, selector=lambda x: x) -> Linq:
        def evaluate(iterable):
            arr = map(selector, iterable)
            yield from itertools.chain.from_iterable(arr)

        return Linq(self, evaluate)

    def select_recursive(self, selector=lambda x: x.nodes) -> Linq:
        def recursive(iterable):
            for item in iterable:
                yield item
                next_iterator = selector(item)
                yield from recursive(next_iterator)

        return Linq(self, recursive)

    def expand(self, expander: Callable[[T], Iterable[R]]) -> Linq[R]:
        """要素からイテレータを生成する関数を引数とし、そのイテレータの要素を展開する。"""

        def evalute(iterable):
            for item in iterable:
                for item2 in expander(item):
                    yield item2

        return Linq(self, evalute)

    def lookup(self, key_selector):
        """指定されたキー セレクター関数および要素セレクター関数に従って、Lookup<TKey,TElement> から IEnumerable<T> を作成します。"""
        # var result = dictionary.ToLookup(item => item.Value[0], item => item.Key);
        raise NotImplementedError()

    def hook(self, func=lambda index, obj: print("{}: {}".format(index, obj))):
        """デバッグ等の目的のために、処理を注入します。map関数ではないため、返されたオブジェクトは無視されます。"""

        def evalute(iterable):
            for index, item in enumerate(iterable):
                func(index, item)
                yield item

        return Linq(self, evalute)

    def hook_if(
        self,
        predicate,
        func=lambda func_name, index, obj: print(f"{func_name} {index}: {obj}"),
    ) -> Linq[T]:
        def evalute(iterable):
            for index, item in enumerate(iterable):
                if predicate(index, item):
                    func(predicate.__name__, index, item)
                yield item

        return Linq(self, evalute)

    def raise_if(
        self,
        predicate,
        exc=lambda func_name, index, obj: ValueError(f"{func_name} {index}: {obj}"),
    ) -> Linq[T]:
        def evalute(iterable):
            for index, item in enumerate(iterable):
                if predicate(index, item):
                    raise exc(predicate.__name__, index, item)
                yield item

        return Linq(self, evalute)

    def raise_if_none(
        self,
        exc=lambda func_name, index, obj: ValueError(f"{func_name} {index}: {obj}"),
    ) -> Linq[T]:
        def deny_none(x):
            return x is None

        return Linq.raise_if(self, predicate=deny_none, exc=exc)

    def default_if_empty(self):
        raise NotImplementedError()

    def repeat(self, count):
        raise NotImplementedError()

    def concat(self, iterable) -> Linq[T]:
        raise NotImplementedError()

    def join(self, iterable) -> Linq[T]:
        raise NotImplementedError()

    def group_join(self) -> Linq[T]:
        raise NotImplementedError()

    def reverse(self) -> Linq[T]:
        return Linq(self, reversed)

    def shuffle(self) -> Linq[T]:
        raise NotImplementedError()

    def order_by_asc(self, func) -> Linq[T]:
        raise NotImplementedError()

    def order_by_desc(self, func) -> Linq[T]:
        raise NotImplementedError()

    def then_by_asc(self) -> Linq[T]:
        raise NotImplementedError()

    def union(self) -> Linq[T]:
        raise NotImplementedError()

    # except
    def difference(self) -> Linq[T]:
        raise NotImplementedError()

    def intersect(self) -> Linq[T]:
        raise NotImplementedError()

    def element_at(self, index) -> Linq[T]:
        raise NotImplementedError()

    def _one_or_undefined(self):
        result = undefined
        for index, item in enumerate(self):
            if index == 0:
                result = item
            if index > 0:
                raise LookupError("element not one.")

        return result

    def one_or_none(self):
        return Linq.one_or_default(self, None)

    def one(self) -> T:
        result = Linq._one_or_undefined(self)
        if result is undefined:
            raise IndexError("element not exists.")

        return result

    def one_or_default(self, default=None):
        result = Linq._one_or_undefined(self)
        if result is undefined:
            result = default

        return result

    def _first_or_undefined(self):
        result = undefined
        for index, item in enumerate(self):
            if index == 0:
                result = item
            break

        return result

    def first_or_none(self):
        return Linq.first_or_default(self, None)

    def first(self):
        result = Linq._first_or_undefined(self)
        if result is undefined:
            raise IndexError("element not exists.")

        return result

    def first_or_default(self, default=None):
        result = Linq._first_or_undefined(self)
        if result is undefined:
            result = default

        return result

    def _last_or_undefined(self):
        result = undefined
        for item in self:
            result = item

        return result

    def last_or_none(self):
        return Linq.last_or_default(self, None)

    def last(self):
        result = self._last_or_undefined()
        if result is undefined:
            raise IndexError("element not exists.")

        return result

    def last_or_default(self, default=None):
        result = self._last_or_undefined()
        if result is undefined:
            result = default

        return result

    # 判定
    def contains(self, predicate) -> bool:
        for item in self:
            if predicate(item):
                return True
        return False

    def all(self) -> bool:
        return all(self)

    def any(self) -> bool:
        return any(self)

    def sequence_equal(self):
        raise NotImplementedError()

    def compare(self, comparison_iterable, fillvalue=undefined) -> Linq[bool]:
        query = Linq(comparison_iterable)

        def evaluate(iterable):
            yield from [
                a == b and type(a) is type(b)
                for a, b in itertools.zip_longest(iterable, query, fillvalue=undefined)
            ]

        return Linq(self, evaluate)  # type: ignore

    # 統計
    # dont implement `__len__`. Please refer to test_python_spec_len
    def len(self) -> int:
        count = 0
        for item in self:
            count += 1

        return count

    def count(self, selector: Callable[[T], R] = None) -> int:
        if selector:
            return self.map(selector).count()
        else:
            return self.len()

    def max(self, selector: Callable[[T], R] = None) -> float:
        if selector:
            return self.map(selector).max()
        else:
            return max(self)

    def min(self, selector: Callable[[T], R] = None) -> float:
        if selector:
            return self.map(selector).min()
        else:
            return min(self)

    def sum(self, selector: Callable[[T], R] = None) -> float:
        if selector:
            return self.map(selector).sum()
        else:
            # XXX: なぜかsum関数だと計算できない
            result = 0
            for item in self:
                result += item
            return result

    def average(self, selector: Callable[[T], R] = None) -> float:
        if selector:
            return self.map(selector).average()
        else:
            # return numpy.mean(self) # -> ひとつの平均しか出さない
            return pd.Series(self).rolling(5, min_periods=1).mean()

    def median(self):
        raise NotImplementedError()

    def mode(self):
        raise NotImplementedError()

    def accumulate(
        self,
        selector: Callable[[T], float] = lambda x: x,
        expression: Callable[[float, float], float] = operator.add,
    ) -> Linq[float]:
        def evalute(iterable):
            query = Linq.map(iterable, selector)
            yield from itertools.accumulate(query, expression)

        return Linq(self, evalute)

    def dispatch(
        self, dispatcher: Callable[[Any], Any]
    ) -> Tuple[int, int, List[Exception]]:
        """要素をファンクションに送出します。例外は無視され、発生した例外はexceptionsに格納されます。

        Args:
            dispatcher (Callable[[Any], Any]): [description]

        Returns:
            Tuple[int, int, List[Exception]]: 0 - count of elements, 1 - succeeded, 2 - exceptions
        """

        succeeded = 0
        exceptions = []

        for item in self:
            try:
                dispatcher(item)
                succeeded += 1
            except Exception as e:
                exceptions.append(e)

        return succeeded + len(exceptions), succeeded, exceptions

    def dispatch_raise(self):
        raise NotImplementedError()

    def each(self, *args: Callable[[Any], Any]) -> NoReturn:
        return Linq.dispatch(self, *args)

    def lazy(self):
        raise NotImplementedError()
        #
        # Linq([1,2,3,4,5,6]).split(3).dispatch(bulkinsert)
        # ↓
        # Linq([1,2,3,4,5,6]).split(3).lazy().dispatch(bulkinsert).do()
        # task = Linq.dummy().split(3).dispatch(bulkinsert)  # dummyはlazy状態になる
        # task.do([1,2,3,4,5,6]) # dummyはlazy状態になる

    # finalizer
    def to(self, factory):
        return factory(self)

    def to_list(self) -> List[T]:
        return list(self)

    def to_tupple(self):
        return tuple(self)

    def to_dict(self):
        return dict(self)

    def to_numpy(self):
        raise NotImplementedError()

    def to_dataframe(self):
        raise NotImplementedError()

    def to_series(self) -> pd.Series:
        return pd.Series(self)

    def to_parse_obj_as(
        self, type_: Type[R], type_name: Optional[NameFactory] = None
    ) -> R:
        """イテレータ全体を指定した型に解釈します。解釈は、pydanticのparse_obj_asを利用します。"""
        return parse_obj_as(type_, self, type_name=type_name)

    def save(self, factory=list) -> Linq[T]:
        """クエリ実行結果をルートイテレータとする新たなインスタンスを作成します。"""
        raise NotImplementedError()

    def attach(self, iterable: Iterable[T]) -> Linq[T]:
        raise NotImplementedError()

    def wrap_send_to(self, func):
        @functools.wraps(func)
        def decorated():
            return func(self())

        return decorated

    def wrap_receive_from(self, func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            return self(result)

        return decorated

    def range(stop: int, start: int = 0, step: int = 1) -> Linq[float]:
        return Linq(range(start=start, stop=stop, step=step))

    @classmethod
    def infinite(cls, func: Callable = lambda: 0) -> "Linq":
        # generatorがきたらどう処理すべきか？
        def create_iterator():
            while True:
                yield func()

        return cls(create_iterator())

    @classmethod
    def from_text(cls):
        raise NotImplementedError()

    @classmethod
    def from_text_line(cls):
        raise NotImplementedError()

    @classmethod
    def from_html(cls):
        raise NotImplementedError()

    @classmethod
    def from_json(cls):
        raise NotImplementedError()

    @classmethod
    def from_csv(cls):
        raise NotImplementedError()

    @classmethod
    def from_yml(cls):
        raise NotImplementedError()

    @classmethod
    def from_xml(cls):
        raise NotImplementedError()

    @classmethod
    def from_toml(cls):
        raise NotImplementedError()

    @classmethod
    def from_excel(cls):
        raise NotImplementedError()

    @classmethod
    def from_glob(cls):
        raise NotImplementedError()

    @staticmethod
    def dummy() -> Linq:
        return LinqDummy()

    # @staticmethod
    # def asyncio(
    #     self: Iterable[Callable[..., Coroutine]]
    # ) -> LinqAsyncio[Callable[..., Coroutine]]:
    #     return LinqAsyncio(self)


class LinqRoot(Linq):
    def __init__(self, __root__: Iterable[T]):
        self.__root__ = __root__
        self.generator_function = iter

    @property
    def _get_type(self) -> Literal["", "root", "dummy"]:
        return "root"


class LinqDummy(Linq):
    def __init__(self):
        self.__root__ = None

    @property
    def _get_type(self) -> Literal["", "root", "dummy", "query"]:
        return "dummy"

    def __iter__(self):
        raise Exception("ダミーオブジェクトはイテレートできません。")


# # TODO: CoroutineをCoroutineFunctionに直す
# class LinqAsyncio(Linq[T]):
#     def __init__(
#         self, __root__: Iterable[Callable[..., Coroutine]], func: Callable = iter
#     ):
#         self.__root__ = convert_to_queryable(__root__)
#         self.generator_function = func

#         if self.__root__ is None:
#             raise ValueError(f"Not queryable: {type(__root__)} {__root__}")

#     def __aiter__(self):
#         return self._serise().__aiter__()

#     async def gather(self: Iterable[Callable[..., Coroutine]]):
#         for co in self:
#             if inspect.iscoroutinefunction(co):
#                 ...
#             else:
#                 ...
#         return await asyncio.gather(*map(lambda x: x(), self))

#     async def _serise(self: Iterable[Callable[..., Coroutine]]):
#         for coroutine_function in self:
#             co = coroutine_function()
#             result = await co
#             yield result

#     def run(self: Iterable[Callable[..., Coroutine]]):
#         coroutine = LinqAsyncio.gather(self)
#         try:
#             return asyncio.run(coroutine)
#         except RuntimeError:
#             raise RuntimeError(
#                 "Cannot be called from a running event loop. Use `gather` instead of `run`."
#             )


# TODO: どっかまともなところへ移す
class MiniDB(Generic[T]):
    def __init__(self):
        self.db = {}

    def key_selector(self, value) -> str:
        return value.__name__.lower()

    def query(self) -> Linq[T]:
        return Linq(self.db.values())

    def get(self, key: str) -> T:
        result = self.db.get(key, None)
        return result

    def add(self, value) -> T:
        key = self.key_selector(value)
        if key is None:
            raise ValueError("Can't add None.")

        if value is None:
            raise ValueError("Can't add None.")

        if key in self.db:
            raise ValueError("Already key exists.")

        self.db[key] = value
        return value
