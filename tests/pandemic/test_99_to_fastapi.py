import json
from typing import Tuple

import pytest
from fastapi import Body, Depends, FastAPI, Query, Security
from fastapi.testclient import TestClient
from pydantic import BaseModel as BA
from pydantic import Field, validator

from pandemic import FastAPI as PandemicAPI
from pandemic import Unpack

fast = FastAPI()
pand = PandemicAPI()

f_client = TestClient(fast)
p_client = TestClient(pand)


class BaseModel(BA):
    class Config:
        allow_population_by_field_name = True


# pandemicの仕様
# 1. Unpack型の引数必須を検知したら、その型のフィールドをクエリパラメータとして公開します
# 2. BaseModelに対してデコレータを利用した場合、暗黙的に__call__をrouterに登録し、selfはリクエストボディもしくはクエリパラメータとして動作します


def test_unpack_query():
    """Unpack型の引数必須を検知したら、その型のフィールドがクエリパラメータとして公開されること"""

    class QueryCommon(BaseModel, Unpack):
        skip: int = 0
        limit: int = 100

    url = "/test_unpack_query"

    @fast.get(url)
    @fast.post(url)
    @fast.put(url)
    @fast.patch(url)
    @fast.delete(url)
    @fast.options(url)
    @fast.head(url)
    @fast.trace(url)
    @pand.get(url)
    @pand.post(url)
    @pand.put(url)
    @pand.patch(url)
    @pand.delete(url)
    @pand.options(url)
    @pand.head(url)
    @pand.trace(url)
    def get_query(common_query: QueryCommon):
        return common_query

    expect = {"skip": 0, "limit": 100}
    assert p_client.get(url).json() == expect
    assert p_client.post(url).json() == expect
    assert p_client.put(url).json() == expect
    assert p_client.patch(url).json() == expect
    assert p_client.delete(url).json() == expect
    assert p_client.options(url).json() == expect
    assert p_client.head(url).status_code == 200
    # p_client.trace(url).json() == expect  # TODO: cant test

    expect = {"skip": 1, "limit": 50}
    query = "?skip=1&limit=50"
    assert p_client.get(url + query).json() == expect
    assert p_client.post(url + query).json() == expect
    assert p_client.put(url + query).json() == expect
    assert p_client.patch(url + query).json() == expect
    assert p_client.delete(url + query).json() == expect
    assert p_client.options(url + query).json() == expect
    assert p_client.head(url + query).status_code == 200
    # p_client.trace(url).json() == expect  # TODO: cant test

    expect = {"skip": "a"}
    query = "?skip=a"
    msg = "value is not a valid integer"
    assert p_client.get(url + query).json()["detail"][0]["loc"] == ["query", "skip"]
    assert p_client.get(url + query).json()["detail"][0]["msg"] == msg
    assert p_client.post(url + query).json()["detail"][0]["msg"] == msg
    assert p_client.put(url + query).json()["detail"][0]["msg"] == msg
    assert p_client.patch(url + query).json()["detail"][0]["msg"] == msg
    assert p_client.delete(url + query).json()["detail"][0]["msg"] == msg
    assert p_client.options(url + query).json()["detail"][0]["msg"] == msg
    assert p_client.head(url + query).status_code == 422
    # assert p_client.trace(url + query) # TODO: cant test

    # fastapi incompatible
    assert f_client.get(url).json()["detail"][0]["loc"] == ["body"]
    assert f_client.get(url).json()["detail"][0]["msg"] == "field required"
    assert f_client.post(url).json()["detail"][0]["msg"] == "field required"
    assert f_client.put(url).json()["detail"][0]["msg"] == "field required"
    assert f_client.patch(url).json()["detail"][0]["msg"] == "field required"
    assert f_client.delete(url).json()["detail"][0]["msg"] == "field required"
    assert f_client.options(url).json()["detail"][0]["msg"] == "field required"
    assert f_client.head(url).status_code == 422
    # assert f_client.trace(url) # TODO: cant test


def test_request_body():
    """UnpackでないBaseModel型の引数必須を検知したら、その型のフィールドがリクエストボディとして公開されること"""

    class BodyCommon(BaseModel):
        name: str
        age: int

    url = "/test_request_body"

    @fast.get(url)
    @fast.post(url)
    @fast.put(url)
    @fast.patch(url)
    @fast.delete(url)
    @fast.options(url)
    @fast.head(url)
    @fast.trace(url)
    @pand.get(url)
    @pand.post(url)
    @pand.put(url)
    @pand.patch(url)
    @pand.delete(url)
    @pand.options(url)
    @pand.head(url)
    @pand.trace(url)
    def get_body(data: BodyCommon):
        return data

    expect = BodyCommon(name="test", age=20).dict()
    body = json.dumps(expect)
    assert p_client.get(url, data=body).json() == expect
    assert p_client.post(url, data=body).json() == expect
    assert p_client.put(url, data=body).json() == expect
    assert p_client.patch(url, data=body).json() == expect
    assert p_client.delete(url, data=body).json() == expect
    assert p_client.options(url, data=body).json() == expect
    assert p_client.head(url, data=body).status_code == 200
    # assert p_client.trace(url).json() == expect  # TODO: cant test

    # fastapi compatible
    assert f_client.get(url, data=body).json() == expect
    assert f_client.post(url, data=body).json() == expect
    assert f_client.put(url, data=body).json() == expect
    assert f_client.patch(url, data=body).json() == expect
    assert f_client.delete(url, data=body).json() == expect
    assert f_client.options(url, data=body).json() == expect
    assert f_client.head(url, data=body).status_code == 200
    # assert f_client.trace(url).json() == expect  # TODO: cant test


def test_depends():
    """Dependsの挙動が変わらないこと"""

    class QueryCommon(BaseModel, Unpack):
        skip: int = 0
        limit: int = 100

    def request_query(skip: int = 0, limit: int = 100):
        return QueryCommon(skip=skip, limit=limit)

    url = "/test_depends"

    @fast.get(url)
    @fast.post(url)
    @fast.put(url)
    @fast.patch(url)
    @fast.delete(url)
    @fast.options(url)
    @fast.head(url)
    @fast.trace(url)
    @pand.get(url)
    @pand.post(url)
    @pand.put(url)
    @pand.patch(url)
    @pand.delete(url)
    @pand.options(url)
    @pand.head(url)
    @pand.trace(url)
    def get_query(common_query: QueryCommon = Depends(request_query)):
        return common_query

    expect = {"skip": 1, "limit": 50}
    query = "?skip=1&limit=50"
    assert p_client.get(url + query).json() == expect
    assert p_client.post(url + query).json() == expect
    assert p_client.put(url + query).json() == expect
    assert p_client.patch(url + query).json() == expect
    assert p_client.delete(url + query).json() == expect
    assert p_client.options(url + query).json() == expect
    assert p_client.head(url + query).status_code == 200
    # p_client.trace(url).json() == expect  # TODO: cant test

    # fastapi compatible
    assert f_client.get(url + query).json() == expect
    assert f_client.get(url + query).json() == expect
    assert f_client.post(url + query).json() == expect
    assert f_client.put(url + query).json() == expect
    assert f_client.patch(url + query).json() == expect
    assert f_client.delete(url + query).json() == expect
    assert f_client.options(url + query).json() == expect
    assert f_client.head(url + query).status_code == 200
    # assert f_client.trace(url) # TODO: cant test


def test_fieldinfo():
    """FieldInfo(QueryやBody)の動作が変わらないこと"""

    url = "/test_query"

    @fast.get(url)
    @fast.post(url)
    @fast.put(url)
    @fast.patch(url)
    @fast.delete(url)
    @fast.options(url)
    @fast.head(url)
    @fast.trace(url)
    @pand.get(url)
    @pand.post(url)
    @pand.put(url)
    @pand.patch(url)
    @pand.delete(url)
    @pand.options(url)
    @pand.head(url)
    @pand.trace(url)
    def request_query(skip: int = Query(0, ge=0)):
        return skip

    query = "?skip=-1"
    msg = "value_error.number.not_ge"
    assert p_client.get(url + query).json()["detail"][0]["type"] == msg
    assert p_client.post(url + query).json()["detail"][0]["type"] == msg
    assert p_client.put(url + query).json()["detail"][0]["type"] == msg
    assert p_client.patch(url + query).json()["detail"][0]["type"] == msg
    assert p_client.delete(url + query).json()["detail"][0]["type"] == msg
    assert p_client.options(url + query).json()["detail"][0]["type"] == msg
    assert p_client.head(url + query).status_code == 422

    assert f_client.get(url + query).json()["detail"][0]["type"] == msg
    assert f_client.post(url + query).json()["detail"][0]["type"] == msg
    assert f_client.put(url + query).json()["detail"][0]["type"] == msg
    assert f_client.patch(url + query).json()["detail"][0]["type"] == msg
    assert f_client.delete(url + query).json()["detail"][0]["type"] == msg
    assert f_client.options(url + query).json()["detail"][0]["type"] == msg
    assert f_client.head(url + query).status_code == 422

    assert p_client.get(url + "?skip=0").status_code == 200
    assert f_client.get(url + "?skip=0").status_code == 200

    url = "/test_field"

    # not support
    with pytest.raises(AttributeError, match="object has no attribute"):

        @fast.get(url)
        def request_query(skip: int = Field(0, ge=0)):
            return skip

    # not support
    with pytest.raises(AttributeError, match="object has no attribute"):

        @pand.get(url)
        def request_query(skip: int = Field(0, ge=0)):
            return skip

    url = "/test_body_1"

    @fast.post(url)
    @pand.post(url)
    def request_body(id: int = Body(...)):
        return id

    # 単一のボディはそれ自体がボディとみなされる
    body = json.dumps(1)
    assert f_client.post(url, data=body).json() == 1
    assert p_client.post(url, data=body).json() == 1

    url = "/test_body_2"

    @fast.post(url)
    @pand.post(url)
    def request_multi_body(id: int = Body(...), name: str = Body(...)):
        return {"id": id, "name": name}

    expect = {"id": 1, "name": "test"}
    body = json.dumps(expect)
    assert f_client.post(url, data=body).json() == expect
    assert p_client.post(url, data=body).json() == expect


def test_pydantic_view():
    """pydantic classの__call__に対して、ルーターがバインドされること"""

    url = "/test_pydantic_view_body"

    @pand.post(url)
    class User(BaseModel):
        name: str
        age: int

        async def __call__(self):
            return self

    expect = {"name": "test", "age": 20}
    body = json.dumps(expect)
    assert p_client.post(url, data=body).json() == expect
    assert p_client.post(url, data=body).status_code == 200

    url = "/test_pydantic_view_query"

    @pand.get(url)
    class CommonQuery(BaseModel, Unpack):
        skip: int = 0
        limit: int = 100

        async def __call__(self):
            return self

    expect = {"skip": 1, "limit": 50}
    assert p_client.get(url + "?skip=1&limit=50").json() == expect
    assert p_client.get(url + "?skip=1&limit=50").status_code == 200

    url = "/test_pydantic_view_path"

    @pand.get(url + "/{skip}")
    class CommonQueryPath(CommonQuery):
        pass

    expect = {"skip": 2, "limit": 50}
    assert p_client.get(url + "/2?limit=50").json() == expect
    assert p_client.get(url + "/2?limit=50").status_code == 200


def test_pydantic_view_has_no_call():
    """pydantic classの__call__がない場合、例外が発生すること"""

    url = "/test_pydantic_view_has_no_call"

    with pytest.raises(AttributeError, match="object has no attribute '__call__'"):

        @pand.post(url)
        class User(BaseModel):
            name: str
            age: int


def test_pydantic_view_doc():
    """関数名が__call__ではなく、クラス名になっていること"""
    url = "/test_pydantic_view_doc"

    @pand.get(url)
    class CreateUser(BaseModel):
        name: str
        age: int

        async def __call__(self):
            return self

    routes = [x for x in pand.routes if x.path == url]
    assert routes[0].dependant.call.__name__ == "CreateUser"


def test_pydantic_validator_body():
    """リクエストボディに対してバリデータが機能していること"""

    class AlreadyExistError(ValueError):
        pass

    class User(BaseModel):
        name: str

        @validator("name")
        def is_exist_name(cls, v):
            raise AlreadyExistError("already exist.")

    url = "/test_pydantic_validator_body"

    @pand.post(url)
    @fast.post(url)
    def create_user(user: User):
        return user

    expect = {"name": ""}
    body = json.dumps(expect)
    msg = "already exist."
    assert p_client.post(url, data=body).json()["detail"][0]["loc"] == ["body", "name"]
    assert p_client.post(url, data=body).json()["detail"][0]["msg"] == msg

    assert f_client.post(url, data=body).json()["detail"][0]["loc"] == ["body", "name"]
    assert f_client.post(url, data=body).json()["detail"][0]["msg"] == msg

    url = "/test_pydantic_validator_body_pydantic_based_view"

    @pand.post(url)
    class User2(User):
        def __call__(self):
            return self

    expect = {"name": ""}
    body = json.dumps(expect)
    msg = "already exist."
    assert p_client.post(url, data=body).json()["detail"][0]["loc"] == ["body", "name"]
    assert (
        p_client.post(url, data=body).json()["detail"][0]["type"]
        == "value_error.alreadyexist"
    )
    assert p_client.post(url, data=body).json()["detail"][0]["msg"] == msg


def test_unpack_query_parameter():
    url = "/test_unpack_query_parameter"

    @pand.get(url)
    class CommonQuery(BaseModel, Unpack):
        skip: int = Query(0, alias="from")
        limit: int = Query(100, alias="size")

        def __call__(self):
            return self

    # パラメータ名誤りはデフォルト値となる
    assert p_client.get(url + "?skip=1&limit=50").json() == {"from": 0, "size": 100}
    assert p_client.get(url + "?from=1&size=50").json() == {"from": 1, "size": 50}


def test_unpack_query_parameter_constraint():
    url = "/test_unpack_query_parameter_constraint"

    @pand.get(url)
    class CommonQuery(BaseModel, Unpack):
        skip: int = Query(0, alias="from", ge=0)
        limit: int = Query(100, alias="size", ge=0)

        def __call__(self):
            return self

    # パラメータ名誤りはデフォルト値となる
    assert p_client.get(url + "?skip=1&limit=50").json() == {"from": 0, "size": 100}
    assert p_client.get(url + "?from=1&size=50").json() == {"from": 1, "size": 50}


def test_todo():
    """TODO: 課題
    1. クエリパラメータ・パスパラメータに対してバリデータを機能させたい
        展開された引数をBaseModelのコンストラクタに渡した際に、例外が発生した場合は、例外はfastapiに通知されない。 -> とても難しい
    """

    url = "/test_pydantic_validator3"

    @pand.get(url)
    class CommonQuery(BaseModel, Unpack):
        skip: int = 0

        @validator("skip")
        def is_not_negative(cls, v):
            if v < 0:
                raise ValueError("must be positive int")
            return v

        def __call__(self):
            return self

    # こうしたい！！
    # assert p_client.post(url).json()["detail"][0]["loc"] == ["query", "skip"]


def create_request_validation():
    """クエリパスパラメータの検証エラーをfastapiに通知したいが、通知方法が分からない。"""
    # fastapi.routing.get_request_handler
    # solved_result = await solve_dependencies(
    #         request=request,
    #         dependant=dependant,
    #         body=body,
    #         dependency_overrides_provider=dependency_overrides_provider,
    #     )
    #     values, errors, background_tasks, sub_response, _ = solved_result
    #     if errors:
    #         raise RequestValidationError(errors, body=body)

    # # fastapi.dependencies.utils
    # solve_dependencies
    #     path_values, path_errors = request_params_to_args(
    #         dependant.path_params, request.path_params
    #     )
    #     query_values, query_errors = request_params_to_args(
    #         dependant.query_params, request.query_params
    #     )
    #     header_values, header_errors = request_params_to_args(
    #         dependant.header_params, request.headers
    #     )
    #     cookie_values, cookie_errors = request_params_to_args(
    #         dependant.cookie_params, request.cookies
    #     )

    # def request_params_to_args(
    #     required_params: Sequence[ModelField],
    #     received_params: Union[Mapping[str, Any], QueryParams, Headers],
    # ) -> Tuple[Dict[str, Any], List[ErrorWrapper]]:

    # v_, errors_ = field.validate(
    #         value, values, loc=(field_info.in_.value, field.alias)
    #     )


# TODO: 前方参照は動かない！
def todo_test_router():
    from pandemic import APIRouter as PandAPIRouter

    router = PandAPIRouter()

    @router.post("/model")
    class User(BaseModel):
        name: str

        async def __call__(self):
            return self

    @router.post("/func")
    def func(user: User):
        return user

    pand.include_router(router, prefix="/users")

    expect = {"name": "test"}
    body = json.dumps(expect)
    assert p_client.post("/users/model", data=body).json() == expect
    assert p_client.post("/users/func", data=body).json() == expect

    class View:
        @router.post("/model2")
        class User(BaseModel):
            name: str

            async def __call__(self):
                return self

    #     @router.post("/func2")
    #     def func(user: User):
    #         return user

    # expect = {"name": "test"}
    # body = json.dumps(expect)
    # assert p_client.post("/users/model2", data=body).json() == expect
    # assert p_client.post("/users/func2", data=body).json() == expect
