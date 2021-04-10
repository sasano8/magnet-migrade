import functools

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.sql.expression import func

# from sqlalchemy.dialects.postgresql import insert


class Crud:
    def __init__(self, obj) -> None:
        self.model = obj

    def get(self, key):
        stmt = select(self.model).where(id == key)
        return QueryEx(stmt=stmt)

    @property
    def query(self) -> "QueryEx":
        stmt = select(self.model)
        return QueryEx(stmt=stmt)

    @property
    def update(self) -> "QueryEx":
        stmt = update(self.model)
        return QueryEx(stmt=stmt)

    @property
    def delete(self) -> "QueryEx":
        stmt = delete(self.model)
        return QueryEx(stmt=stmt)

    @property
    def create(self) -> "QueryEx":
        stmt = insert(self.model)
        return QueryEx(stmt=stmt)

    @property
    def upsert(self) -> "QueryEx":
        pass

    @property
    def copy(self) -> "QueryEx":
        pass


class QueryEx:
    def __init__(self, stmt: Select, mapper=None):
        self.stmt = stmt
        self.mapper = mapper

    def where(self, *criterion):
        stmt = self.stmt.where(*criterion)
        return self.__class__(stmt=stmt, mapper=self.mapper)

    def values(self, **kwargs):
        stmt = self.stmt.values(**kwargs)
        return self.__class__(stmt=stmt, mapper=self.mapper)

    def select(self):
        pass

    def map(self, out):
        # db.execute().columns(model)  # orm モデルが返る
        # db.execute(select(model)).scalars()  # orm モデルが返る　もしくは　先頭の列が返る
        # db.execute(select(User).where(User.id == 3)).raw namedtupleがカエルっぽい
        def parse(result):
            for dic in result.raw:
                yield dic

        if self.mapper:
            raise Exception()

        return self.__class__(stmt=self.stmt, mapper=parse)

    def execute(self, db: Session):
        result = db.execute(self.stmt)
        if self.mapper is None:
            return result
        return self.mapper(result)

    def all(self, db: Session):
        return list(self.execute(db))

    def one(self, db):
        return self.execute(db).one()

    def one_or_none(self, db):
        return self.execute(db).one_or_none()

    def one_or_404(self, db):
        obj = self.execute(db).one_or_none()
        if not obj:
            raise KeyError()
        return obj

    def count(self, db) -> int:
        stmt = self.stmt.select(func.count())
        return db.execute(stmt).scalar()

    def exists(self, db) -> bool:
        return db.execute(self.stmt.exists()).scalar()


class Queryable:
    @classmethod
    @functools.lru_cache
    def sql(cls) -> Crud:
        return Crud(cls)
