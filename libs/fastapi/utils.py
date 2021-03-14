from enum import Enum
from typing import Any, Generic, Iterable, List, Literal, Tuple, Type, TypeVar, Union

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import (
    BaseModel,
    Field,
    PydanticValueError,
    ValidationError,
    validate_arguments,
    validator,
)
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Query, Session
from sqlalchemy.orm.session import make_transient
from sqlalchemy.sql.schema import Column


def paginate(query: Query, page: int, items_per_page: int):
    # Never pass a negative OFFSET value to SQL.
    offset_adj = 0 if page <= 0 else page - 1
    items = query.limit(items_per_page).offset(offset_adj * items_per_page).all()
    total = query.order_by(None).count()
    return items, total


Alchemy = TypeVar("Alchemy")


class EnumBase(Enum):
    """define enum with key-value.  EXAMPLE: FIRST = 0, 'first',"""

    def __str__(self):
        return self.msg

    @property
    def no(self):
        return self._value_[0]

    @property
    def msg(self):
        return self._value_[1]


class EMsg(EnumBase):
    E_001_NOT_PERMITTED = 1, "extra fields not permitted"
    E_002_NOT_EDIT = 2, "fields not permitted editing"


class EType(EnumBase):
    E_001_VAL_ERR_MISSING = 1, "value_error.missing"
    E_002_VAL_ERR_IMMUTABLE = 2, "value_error.immutable"


class ExcBuilder:
    def __init__(self, status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        self.status_code = status_code
        self.errors = []

    def add(
        self,
        loc: tuple,
        msg: EnumBase,
        type_: EnumBase,
    ):
        self.errors.append({"loc": loc, "msg": msg.__str__(), "type": type_.__str__()})

    def build(self):
        return HTTPException(status_code=self.status_code, detail=self.errors)


@validate_arguments
def build_exception(
    loc: tuple,
    msg: str,
    # type_: str,
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        # detail=[{"loc": loc, "msg": msg, "type": type_}]
        detail=[{"loc": loc, "msg": msg}],
    )


class GenericRepository(Generic[Alchemy]):
    def __init__(self, db: Session = None):
        self.model: Type[Alchemy] = self.get_model()
        self.primary_keys: List[Column] = self._get_primary_keys(self.model)
        self.db = db

    @classmethod
    def get_model(cls) -> Type[Alchemy]:
        generic_type = cls.__orig_bases__[0].__args__[0]
        return generic_type

    @classmethod
    def _get_primary_keys(cls, table):
        tuple = inspect(table).primary_key
        return list(tuple)

    def contais_primary_key(self, data: BaseModel):
        for field in self.primary_keys:
            if hasattr(data, field.name):
                if data[field.name] is not None:
                    return True
        return False

    def build_primary_keys_criterion(self, data: dict):
        m = self.model
        conditions = []
        for field in self.primary_keys:
            col = getattr(m, field.name)
            val = data[field.name]
            conditions.append(col == val)
        if len(conditions) == 0:
            raise Exception()
        return False

    def select(self, *fields):
        return self.db.query(*fields)

    def filter(self, *criterion):
        return self.db.query(self.model).filter(*criterion)

    # TOOD: filterに統合する
    def query(self, *criterion) -> Union[Query, Iterable[Alchemy]]:
        return self.db.query(self.model).filter(*criterion)

    def get(self, id: int) -> Alchemy:
        # criterion = self.build_primary_keys_criterion(dict(id=id))
        return self.query().filter(self.model.id == id).one_or_none()

    def create(self, data: BaseModel) -> Alchemy:
        dic = data.dict()
        if self.contais_primary_key(dic):
            raise ValueError("create時にprimary keyを含めることはできません。")

        obj = self.model(**dic)
        db = self.db
        db.add(obj)
        db.commit()
        db.refresh(obj)

        # トランザクション管理を極めてきたら、get_dbにauto commitを追加して、こっちにすればいいかも。
        # db.add(obj)  # 登録予約する。
        # db.flush  # SQLをデータベースに送信し、オブジェクトの状態を更新する。commit操作が最終的に必要。
        return obj

    def update(self, data: BaseModel) -> Alchemy:
        # TODO: 自動キー検出を設ける
        obj = self.query().filter(self.model.id == data.id).one_or_none()
        if obj is None:
            return None
        dic = data.dict(exclude_unset=True)  # 未設定の価は更新しない
        # TODO: モデルに属性が定義されていない場合、存在しない属性は無視されてしまう？
        [setattr(obj, k, v) for k, v in dic.items()]
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def upsert(self, data: BaseModel) -> Alchemy:
        obj = self.update(data)
        if obj:
            return obj
        # TODO: idがコピーされるため、除外した方がよい？
        obj = self.model(**data.dict())
        db = self.db
        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def delete(self, id: int) -> int:
        count = self.query().filter(self.model.id == id).delete()
        # count = self.query(self.model.id == id).delete()
        self.db.commit()
        return count

    def delete_all(self) -> int:
        count = self.query().delete()
        self.db.commit()
        return count

    def put(self, data: BaseModel) -> Alchemy:
        self.query().filter(self.model.id == data.id).delete()
        # self.query(self.model.id == data.id).delete()
        obj = self.create(data)
        return obj

    def duplicate(self, id: int) -> Alchemy:
        obj = self.get(id)
        if obj is None:
            return None

        self.db.expunge(obj)  # セッションからオブジェクトを除外する
        obj.id = None
        make_transient(obj)  # オブジェクトを一時的なものにする。よく分からない。
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def bulk_insert(
        self, rows: Iterable[BaseModel], auto_commit=True
    ) -> Tuple[int, int]:
        model = self.model
        try:
            deleted = 0
            inserted = 0

            for item in rows:
                obj = model(**item.dict())
                self.db.add(obj)
                inserted += 1

            if auto_commit:
                self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise

        return deleted, inserted

    def bulk_delete_insert(
        self, delete_query: Query, rows: Iterable[dict], auto_commit=True
    ) -> Tuple[int, int]:
        # TODO: トランザクション操作はおこないわないようにする
        model = self.model

        try:
            deleted = delete_query.delete()
            inserted = 0

            for row in rows:
                obj = model(**row)
                self.db.add(obj)
                inserted += 1

            if auto_commit:
                self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise

        return deleted, inserted


Repository = TypeVar("GenericRepository[Alchemy]", bound=GenericRepository[Alchemy])


class CommonQuery(BaseModel):
    skip: int = Field(0, alias="from")
    limit: int = 100
    query: dict = {}


class TemplateView(Generic[Repository]):
    """汎用的に利用する機能をテンプレート化する。独自にAPIを実装する場合は、無理に当該クラスを継承せず、直接API実装箇所に実装してしまえばよい。"""

    # def __init__(self):
    #     # fastapi-utils cvsが依存性定義に応じて、自動でコンストラクタを作成する。
    #     # クラス初期化時に、キーワード引数で初期化引数にアクセスすることができる。

    @property
    def db(self) -> Session:
        raise NotImplementedError()

    @classmethod
    def get_repository(cls) -> Type[Repository]:
        """継承時に指定したsqlalchemyクラスを取得します。多分、２回以上継承すると動かない。"""
        generic_type = cls.__orig_bases__[0].__args__[0]
        return generic_type

    @property
    def rep(self) -> Repository:
        repository = self.get_repository()
        return repository(self.db)

    def query(self, query: CommonQuery) -> List[Alchemy]:
        rep = self.rep
        m = rep.model
        criterion = []
        for key in query.query.keys():
            field = getattr(self, key, None)
            if not field:
                Exception("想定していないフィールドです。")
            cond = field == query.query[key]
            criterion.append(cond)

        return list(rep.query(*criterion).offset(query.skip).limit(query.limit))

    def index(self, skip: int = 0, limit: int = 100) -> List[Alchemy]:
        results = self.rep.query().offset(skip).limit(limit)
        return list(results)

    def get(self, id: int) -> Alchemy:
        result = self.rep.get(id=id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return result

    def create(self, data: BaseModel) -> Alchemy:
        result = self.rep.create(data=data)
        return result

    def delete(self, id: int) -> int:
        result = self.rep.delete(id=id)
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return result

    def patch(self, id: int, data: BaseModel) -> Alchemy:
        if hasattr(data, "id") and data.id is not None and data.id != id:
            e = ExcBuilder(status.HTTP_422_UNPROCESSABLE_ENTITY)
            e.add(("id",), EMsg.E_002_NOT_EDIT, EType.E_002_VAL_ERR_IMMUTABLE)
            raise e.build()
        obj = data.copy()
        obj.id = id
        result = self.rep.update(obj)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return result

    def duplicate(self, id: int) -> Alchemy:
        result = self.rep.duplicate(id=id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return result
