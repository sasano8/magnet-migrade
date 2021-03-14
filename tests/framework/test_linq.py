# type: ignore

import itertools
import operator

import pytest

from framework.utils.linq import Linq, convert_to_queryable


def assert_same_iterator(query):
    """
    イテレータは何度でも同じ結果を返すことを確認。
    """
    arr1 = query.to_list()
    arr2 = query.to_list()

    for index, item in enumerate(arr1):
        assert arr1[index] == arr2[index]


def test_builtin_generator():
    """一度消費したイテレータを再利用すると、イテレートされないことを確認する。"""

    def assert_builtin_iterator(query):
        arr1 = list(query)
        arr2 = list(query)

        assert len(arr1) > 0, "0件以上のデータが返るイテレータを渡してください。"
        assert len(arr2) == 0

    arr = [1, 2, 3, 4, 5]
    assert_builtin_iterator(map(lambda x: "a", arr))
    assert_builtin_iterator(filter(lambda x: x % 2 == 0, arr))
    assert_builtin_iterator(itertools.islice(arr, 3))
    assert_builtin_iterator(itertools.filterfalse(lambda x: x % 2 == 0, arr))
    assert_builtin_iterator(itertools.takewhile(lambda x: x < 3, arr))
    assert_builtin_iterator(itertools.dropwhile(lambda x: x < 3, arr))
    assert_builtin_iterator(reversed(arr))
    assert_builtin_iterator(zip(arr))
    assert_builtin_iterator(itertools.zip_longest(arr))
    assert_builtin_iterator(itertools.chain.from_iterable(["abc", "def"]))
    assert_builtin_iterator(itertools.accumulate(arr, operator.add))
    # assert_builtin_iterator(numpy.mean(arr))


def test_bultin_aggregate():
    arr = [1, 2, 3]
    result = itertools.accumulate(arr, operator.add)
    assert all([a == b for a, b in itertools.zip_longest(result, [1, 3, 6])])


def test_python_spec_len():
    class NonSizedIterator:
        def __init__(self, iterator):
            self.iterator = iterator

        def __iter__(self):
            return self.iterator

    class SizedIterator:
        def __init__(self, iterator):
            self.iterator = iterator

        def __iter__(self):
            return self.iterator

        def __len__(self):
            count = 0
            for item in self:
                count += 1
            return count

    def iterate():
        yield 1
        yield 2

    it = iterate()
    query = NonSizedIterator(it)
    arr_1 = list(query)

    it = iterate()
    query = SizedIterator(it)
    arr_2 = list(query)

    assert len(arr_1) == 2
    assert len(arr_2) == 0  # リスト生成時にlenが検証されるため、イテレータが消費され、空リストが返る


def test_linq_init():
    query = Linq([1, 2, 3])
    assert all([a == b for a, b in itertools.zip_longest(query.__root__, [1, 2, 3])])
    assert not hasattr(query, "__len__")  # test_python_spec_len 参照


class InfinityIterable:
    def __getitem__(self, index):
        return index


def iterate():
    yield 1
    yield 2


@pytest.mark.parametrize(
    "instance",
    [
        (iterate, True),
        (iterate(), True),
        (filter(lambda x: True, []), True),
        (map(lambda x: x, []), True),
        (list(), True),
        (dict(), True),
        (tuple(), True),
        (set(), True),
        (frozenset(), True),
        (str(""), True),
        (InfinityIterable(), True),
        (None, False),
        (lambda x: x, False),
        (int(1), False),
    ],
)
def test_linq_accetable(instance):
    obj, expected = instance[0], instance[1]
    converted = convert_to_queryable(obj)
    if converted is None:
        assert not expected
        with pytest.raises(ValueError) as e:
            assert Linq(obj)
    else:
        assert expected
        assert Linq(obj)


def test_linq_base():
    assert bool(True)
    assert bool(1)
    assert bool(-1)
    assert bool("a")
    assert not bool(False)
    assert not bool(0)
    assert not bool(None)
    assert not bool("")

    # True
    src = []
    assert Linq(src).all() == all(src)

    # True
    src = [True]
    assert Linq(src).all() == all(src)

    # False
    src = [False]
    assert Linq(src).all() == all(src)

    # False
    src = [None]
    assert Linq(src).all() == all(src)


def test_linq_compare():
    obj0 = {}
    obj1 = {}
    obj2 = {"name": "test"}
    source = [
        [0, None, True, obj0],
        [None, None, True, obj0],
        [False, None, True, obj0],
        [0, None, True, obj1],
        [0, None, True, obj2],
    ]

    query = Linq(source[0])
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(query.__root__, [0, None, True, obj0])
        ]
    )
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(
                query.compare(source[0]), [True, True, True, True]
            )
        ]
    )
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(
                query.compare(source[1]), [False, True, True, True]
            )
        ]
    )
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(
                query.compare(source[2]), [False, True, True, True]
            )
        ]
    )
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(
                query.compare(source[3]), [True, True, True, True]
            )
        ]
    )
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(
                query.compare(source[4]), [True, True, True, False]
            )
        ]
    )

    obj0 = [0, 1, None]
    obj1 = [0, 1, None]
    obj2 = [0, 1]
    source = [
        [obj0],
        [obj1],
        [obj2],
    ]

    query = Linq(source[0])
    assert all(
        [a == b for a, b in itertools.zip_longest(query.compare(source[0]), [True])]
    )
    assert all(
        [a == b for a, b in itertools.zip_longest(query.compare(source[1]), [True])]
    )
    assert all(
        [a == b for a, b in itertools.zip_longest(query.compare(source[2]), [False])]
    )

    source = [
        [0, None],
        [0],
    ]

    class Undefined:
        pass

    undefined = Undefined()

    query = Linq(source[0])
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(query.compare(source[0]), [True, True])
        ]
    )
    assert all(
        [
            a == b
            for a, b in itertools.zip_longest(query.compare(source[1]), [True, False])
        ]
    )


def test_dict():
    dic = {1: -1, 2: -2, 3: -3}
    linq = Linq(dic)

    query = linq
    assert_same_iterator(query)
    assert query.compare(list(dic.items())).all()  # dictは暗黙的にdic.items()と解釈されます
    assert query.compare({1: -1, 2: -2, 3: -3}).all()
    assert query.compare([(1, -1), (2, -2), (3, -3)]).all()  # キーバリュータプルと同等です
    assert not query.compare({1: -1, 2: -2, 3: -4}).all()
    assert query.compare(query.to_dict()).all()
    assert Linq(list(dic)).compare([1, 2, 3]).all()

    query = Linq(linq.to_list())
    assert_same_iterator(query)
    assert query.compare([(1, -1), (2, -2), (3, -3)]).all()
    assert not query.compare([(1, -1), (2, -2), (3, -4)]).all()
    assert query.compare(query.to_list()).all()


def test_side_effect():
    arr = []
    query = Linq(arr)
    assert query.len() == 0

    arr.append(1)
    assert query.len() == 1

    dic = {}
    query = Linq(dic)
    assert query.len() == 0

    dic[0] = 1
    assert query.len() == 1


def test_linq():

    arr = [1, 2, 3]
    linq = Linq(arr)

    query = linq.filter(lambda x: x % 2 == 0)
    assert_same_iterator(query)

    query = linq.map(lambda x: x * 2)
    assert_same_iterator(query)

    query = linq.filter(lambda x: x % 2 == 0).filter(lambda x: False)
    assert_same_iterator(query)
    assert query.len() == 0

    query = linq.map(lambda x: x * 2).map(lambda x: x * 2)
    assert_same_iterator(query)
    assert query.compare([4, 8, 12]).all()

    query = linq.skip(1).map(lambda x: x * 2)
    assert_same_iterator(query)
    assert query.len() == 2
    assert query.compare([4, 6]).all()

    query = linq.slice(1).map(lambda x: x * 2)
    assert_same_iterator(query)
    assert query.len() == 2
    assert query.compare([4, 6]).all()

    query = linq.slice(0, 2).map(lambda x: x * 2)
    assert_same_iterator(query)
    assert query.len() == 2
    assert query.compare([2, 4]).all()

    query = linq.slice(0, 3, 2).map(lambda x: x * 2)
    assert_same_iterator(query)
    assert query.len() == 2
    assert query.compare([2, 6]).all()

    query = Linq(["abc", "def"]).select_many()
    assert_same_iterator(query)
    assert query.compare(["a", "b", "c", "d", "e", "f"]).all()

    query = Linq([{"name": "abc"}, {"name": "def"}]).select_many(lambda x: x["name"])
    assert_same_iterator(query)
    assert query.compare(["a", "b", "c", "d", "e", "f"]).all()

    # query = Linq(arr).map(lambda x: x).accumulate().map(lambda x: x)
    # assert_same_iterator(query)
    # assert all([a == b for a, b in itertools.zip_longest(list(query), [1, 3, 6])])


def test_iterator():
    def iterate():
        yield 1
        yield 2

    it = iterate()
    query_1 = Linq(it)
    arr = list(query_1)
    print(arr)
    assert Linq(arr).compare([1, 2]).all()
