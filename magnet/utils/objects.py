from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Generic,
    Iterable,
    List,
    Literal,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    Union,
    abstractmethod,
    get_args,
    runtime_checkable,
)

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, event, inspect, or_, select, update
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query, Session, load_only, make_transient
from sqlalchemy.sql.expression import insert

from framework import undefined

T = TypeVar("T")


# dummy
class CommonQuery:
    pass


@runtime_checkable
class PRepository(Protocol[T]):
    @classmethod
    @lru_cache
    def as_model(cls) -> Type[T]:
        model: Type[T] = get_args(cls.__orig_bases__[0])[0]
        return model

    @classmethod
    def as_service(cls):
        model = cls.as_model()
        if TYPE_CHECKING:
            return cls
        else:
            # return model.as_service()  # type: ignore
            class Service(ServiceBase[model]):
                pass

            return Service

    @staticmethod
    def query(db: Session, /) -> "Query[T]":
        raise NotImplementedError()

    @staticmethod
    def index(db: Session, /, skip: int = 0, limit: int = 100) -> "Query[T]":
        raise NotImplementedError()

    @staticmethod
    def get(db: Session, *, id: int) -> Union[T, None]:
        raise NotImplementedError()

    @staticmethod
    def create(db: Session, **data) -> T:
        """レコードを作成する。idの指定は許容されない。"""
        raise NotImplementedError()

    @staticmethod
    def insert(db: Session, **data):
        """レコードを作成する。idの指定が許容される。idが指定されない場合は、新たなidが発行される"""
        raise NotImplementedError()

    @staticmethod
    def update(db: Session, **data) -> Union[T, None]:
        """レコードが存在する場合は、そのレコードを部分更新する。"""
        raise NotImplementedError()

    @staticmethod
    def upsert(db: Session, **data) -> Union[T, None]:
        """レコードが存在する場合は、そのレコードを更新する。存在しない場合は、レコードを作成する。"""
        raise NotImplementedError()

    @staticmethod
    def put(db: Session, **data) -> T:
        """指定されたidのレコードを、新たなデータでレコードを完全に置き換える。"""
        raise NotImplementedError()

    @staticmethod
    def delete(db: Session, *, id: int) -> int:
        """指定されたidのレコードを削除する"""
        raise NotImplementedError()

    @staticmethod
    def duplicate(db: Session, *, id: int) -> Union[T, None]:
        """指定されたidのレコードを複製する"""
        raise NotImplementedError()

    @staticmethod
    def bulk_insert(db: Session, *, rows: Iterable[dict]):
        raise NotImplementedError()


class RepositoryBase(PRepository[T]):
    def __init__(self, model: Type[T]) -> None:
        raise RuntimeError("can't instatntiate.")

    @classmethod
    def query(cls, db: Session, /) -> "Query[T]":
        return db.query(cls.as_model())

    @classmethod
    def index(cls, db: Session, /, skip: int = 0, limit: int = 100) -> "Query[T]":
        return db.query(cls.as_model()).offset(skip).limit(limit)

    @classmethod
    def exist(cls, db: Session, *, id: int) -> bool:
        m = cls.as_model()
        obj = db.query(m.id).filter(m.id == id).one_or_none()  # type: ignore
        return obj is not None

    @classmethod
    def get(cls, db: Session, *, id: int) -> Union[T, None]:
        m = cls.as_model()
        return db.query(m).filter(m.id == id).one_or_none()

    @classmethod
    def create(cls, db: Session, **data) -> T:
        """レコードを作成する。idの指定は許容されない。"""
        id = data.pop("id", None)
        if id is not None:
            raise ValueError("create時にprimary keyを含めることはできません。")
        obj = cls.insert(db, **data)
        return obj

    @classmethod
    def insert(cls, db: Session, **data) -> T:
        """レコードを作成する。idの指定が許容される。idが指定されない場合は、新たなidが発行される"""
        obj = cls.as_model()(**data)
        db.add(obj)
        db.flush()  # データをプッシュする
        return obj

    @classmethod
    def update(cls, db: Session, *, id: int, **data) -> Union[T, None]:
        """deprecated. use patch."""
        return cls.patch(db, id=id, **data)

    @classmethod
    def patch(cls, db: Session, *, id: int, **data) -> Union[T, None]:
        """レコードが存在する場合は、そのレコードを部分更新する。"""
        # if not "id" in data:
        #     raise KeyError("idを指定してください")
        obj = cls.get(db, id=id)
        if obj is None:
            return None
        # TODO: モデルに属性が定義されていない場合、存在しない属性は無視されてしまう？
        [setattr(obj, k, v) for k, v in data.items()]
        db.flush()  # データをプッシュし、idを発行する。ただし、確定するのはコミット時
        return obj

    @classmethod
    def upsert(cls, db: Session, *, id: int, **data) -> Union[T, None]:
        """レコードが存在する場合は、そのレコードを部分更新する。存在しない場合は、レコードを作成する。"""
        obj = cls.patch(db, id=id, **data)
        if obj:
            return obj
        return cls.insert(db, id=id, **data)

    @classmethod
    def put(cls, db: Session, *, id: int, **data) -> T:
        """指定されたidのレコードを、新たなデータでレコードを完全に置き換える。"""
        if id is not None:
            m = cls.as_model()
            count = db.query(m).filter(m.id == id).delete()
        obj = cls.insert(db, id=id, **data)
        return obj

    @classmethod
    def delete(cls, db: Session, *, id: int) -> int:
        """指定されたidのレコードを削除する"""
        m = cls.as_model()
        count = db.query(m).filter(m.id == id).delete()
        return count

    @classmethod
    def duplicate(cls, db: Session, *, id: int) -> Union[T, None]:
        """指定されたidのレコードを複製する"""
        obj = cls.get(db, id=id)
        if obj is None:
            return None

        db.expunge(obj)  # セッションからオブジェクトを除外する
        obj.id = None  # type: ignore
        make_transient(obj)  # セッションから切り離し、primary keyを消去する。expungeとNoneのセットいらないかも
        db.add(obj)
        db.flush()  # データをプッシュし、idを発行する。ただし、確定するのはコミット時
        return obj

    @classmethod
    def bulk_insert(cls, db: Session, *, rows: Iterable[dict]):
        raise NotImplementedError()


class PService(Protocol[T]):
    """汎用的に利用する機能をテンプレート化する。独自にAPIを実装する場合は、無理に当該クラスを継承せず、直接API実装箇所に実装してしまえばよい。"""

    def __init__(self):
        raise RuntimeError("can't instatntiate.")

    @classmethod
    @lru_cache
    def as_model(cls) -> Type[T]:
        model: Type[T] = cls.__orig_bases__[0].__args__[0]
        return model

    @classmethod
    def as_rep(cls) -> Type[RepositoryBase[T]]:
        """継承時に指定したsqlalchemyクラスを取得します。多分、２回以上継承すると動かない。"""
        model: Type[T] = cls.as_model()
        return model.as_rep()

    @abstractmethod
    def query(db: Session, *args, **kwargs) -> List[T]:
        raise NotImplementedError()

    @abstractmethod
    def index(db: Session, *, skip: int = 0, limit: int = 100) -> List[T]:
        raise NotImplementedError()

    @abstractmethod
    def get(db: Session, *, id: int) -> T:
        raise NotImplementedError()

    @abstractmethod
    def create(db: Session, **data) -> T:
        raise NotImplementedError()

    @abstractmethod
    def insert(db: Session, **data) -> T:
        raise NotImplementedError()

    @abstractmethod
    def delete(db: Session, *, id: int) -> int:
        raise NotImplementedError()

    @abstractmethod
    def put(db: Session, **data) -> T:
        raise NotImplementedError()

    @abstractmethod
    def patch(db: Session, **data) -> T:
        raise NotImplementedError()

    @abstractmethod
    def duplicate(db: Session, *, id: int) -> T:
        raise NotImplementedError()


class ServiceBase(PService[T]):
    """基本的なレポジトリ操作の検証を行います。"""

    # @classmethod
    # def query(cls, db: Session, *, query: CommonQuery) -> List[T]:
    #     m = cls.as_model()
    #     rep = cls.as_rep()
    #     criterion = []
    #     for key in query.query.keys():
    #         field = getattr(m, key, None)
    #         if not field:
    #             Exception("想定していないフィールドです。")
    #         cond = field == query.query[key]
    #         criterion.append(cond)

    #     return list(
    #         rep.query(db).filter(*criterion).offset(query.skip).limit(query.limit)
    #     )

    @classmethod
    def query(cls, db: Session, *args, **kwargs) -> List[T]:
        query = cls.as_rep().query(db, *args, **kwargs)
        if not query:
            raise RuntimeError("must be return response.")
        return query

    @classmethod
    def index(cls, *args, **kwargs) -> "Query[T]":
        query = cls.as_rep().index(*args, **kwargs)
        if not query:
            raise RuntimeError("must be return response.")
        return query

    @classmethod
    def get(cls, *args, **kwargs) -> T:
        result = cls.as_rep().get(*args, **kwargs)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return result

    @classmethod
    def create(cls, *args, **kwargs) -> T:
        result = cls.as_rep().create(*args, **kwargs)
        if not result:
            raise RuntimeError("must be return response.")
        return result

    @classmethod
    def insert(cls, *args, **kwargs) -> T:
        result = cls.as_rep().insert(*args, **kwargs)
        if not result:
            raise RuntimeError("must be return response.")
        return result

    @classmethod
    def delete(cls, *args, **kwargs) -> int:
        result = cls.as_rep().delete(*args, **kwargs)
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return result

    @classmethod
    def patch(cls, *args, **kwargs) -> T:
        # if not "id" in data:
        #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        result = cls.as_rep().patch(*args, **kwargs)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return result

    @classmethod
    def put(cls, *args, **kwargs):
        result = cls.as_rep().put(*args, **kwargs)
        if not result:
            raise RuntimeError("must be return response.")
        return result

    @classmethod
    def duplicate(cls, *args, **kwargs) -> T:
        result = cls.as_rep().duplicate(*args, **kwargs)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return result


def Service(rep: T) -> T:
    if not issubclass(rep, PRepository):
        raise TypeError()
    model = rep.as_model()

    class Service(ServiceBase[model]):
        pass

    return Service


class MyQuery(Query):
    """criterionにundefinedを与えた時、そのバイナリオペレータは無視される"""

    @staticmethod
    def _exclude_undefined(criterion):
        arr = []
        for be in criterion:
            do_append = True
            # バイナリエクスプレッションは比較するとコンパイルが生じる特殊な動作になっているので、比較しないように処理する
            right = getattr(be, "right", None)
            if value := getattr(right, "value", None):
                if value is undefined:
                    do_append = False

            if do_append:
                arr.append(be)
        return arr

    def select(self, select: Iterable[str] = None) -> "Query[T]":
        if not select:
            return self
        else:
            return self.options(load_only(*select))

    # 現在の処理では複雑なバイナリオペレータに対応していないので、filterのオーバーライドは避ける
    def where(self, *criterion):
        new = self._exclude_undefined(criterion)
        return super().filter(*new)

    def where_or(self, *criterion):
        new = self._exclude_undefined(criterion)
        return super().filter(or_(*new))

    def where_by(self, **kwargs):
        excludes = set()
        for k, v in kwargs.items():
            if v is undefined:
                excludes.add(v)
        for k in excludes:
            del kwargs[k]
        return super().filter_by(**kwargs)


from inflector import Inflector


class Entity:
    @declared_attr
    def __tablename__(cls):
        """クラス名からスネークケースのテーブル名を生成する"""
        inflector = Inflector()
        return inflector.tableize(cls.__name__)
        # names = re.split("(?=[A-Z])", cls.__name__)  # noqa
        # return "_".join([x.lower() for x in names if x])

    @classmethod
    def __declare_last__(cls):
        """
        configure_mappers呼び出し時に、いくつかのtable_argsを自動で設定する。
        - comment: クラスのdocstringを自動で設定
        """
        dic = cls.__table__.__dict__
        # docstringをテーブルのコメントとする
        if dic.get("comment", None) is None:
            if cls.__doc__:
                dic["comment"] = cls.__doc__

    @classmethod
    def select(cls, *columns: Union[str, Column]) -> select:
        if columns:
            return select(cls).options(load_only(*columns))
        else:
            return select(cls)

    def create(self, db: Session):
        """インスタンスを作成し、フラッシュする。idなどが発行されるが、コミットまで状態は確定していない。"""
        db.add(self)
        db.flush()
        return self

    def update(self, db: Session, **update):
        """インスタンスを更新し、他オブジェクトも含む変更をデータベースにフラッシュする。コミットまで状態は確定しない。"""
        if inspect(self).transient:
            raise Exception("セッションに参加していないオブジェクトに対して更新を行うことはできません")
        [setattr(self, k, v) for k, v in update.items()]  # type: ignore
        db.flush()
        return self

    def identify(self):
        """自身を特定するcriterionを返します"""
        if self.id is None:
            raise KeyError("データベースレコードを特定できません。インスタンスのidはNoneです。")
        return self.__class__.id == self.id

    @property
    def stmt_update(
        self,
        # **values,
        # synchronize_session: Literal[
        #     False, "fetch", "evaluate"
        # ] = False,  # Falseはメモリ内オブジェクトを同期しない
    ):
        """update文のwhereを組み立てます。なお、valuesを複数使用すると値は最後の値が有効になります。"""
        return (
            update(self.__class__)
            .where(self.identify)
            .execution_options(synchronize_session=False)
            .values
        )

    def delete(self, db: Session) -> Literal[1]:
        """インスタンスを削除し、他オブジェクトも含む変更をデータベースにフラッシュする。コミットまで状態は確定しない。"""
        db.delete(self)
        db.flush()
        return 1

    @classmethod
    def to_query(cls: Type[T], db: Session, select: Iterable[str] = None) -> "Query[T]":
        if not select:
            return db.query(cls)
        else:
            return db.query(cls).options(load_only(*select))

    @classmethod
    def as_rep(cls: Type[T]) -> Type[RepositoryBase[T]]:
        class Repositroy(RepositoryBase[cls]):
            pass

        return Repositroy

    @classmethod
    def as_service(cls: Type[T]) -> Type[ServiceBase[T]]:
        # class Service(ServiceBase[cls]):
        #     pass

        # return Service
        return cls.as_rep().as_service()

    def dict(self, excludes=set()):
        dic = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        for name in excludes:
            dic.pop(name, None)
        return dic


# def update_tarble_args(cls: Type[Entity]):
#     @event.listens_for(cls, "class_instrument")
#     def __update_table_args__(cls):
#         dic = cls.__table__.__dict__

#         if dic.get("comment", None) is None:
#             if cls.__doc__:
#                 dic["comment"] = cls.__doc__
