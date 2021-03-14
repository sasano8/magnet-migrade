import functools
from typing import Any, Literal, Type

from pydantic import BaseModel

from framework.analyzers import AnyAnalyzer
from framework.converters import Converter


# TODO: モデルの作成まではやらずに辞書を作るところまでに抽象化すれば処理を共通化できるのでは
def convert_to_func_code_from_pydantic(
    cls: Type[BaseModel], as_method=False, dependencies=None
):
    bind_func_name = "tmp_func"
    bind_model_name = "Model"

    annotations = {}
    defaults = []
    kwdefaults = {}

    fields_required = []
    fields_non_required = []

    # sort required first
    for field in cls.__fields__.values():
        if field.required:
            fields_required.append(field)
        else:
            fields_non_required.append(field)

    fields = fields_required
    fields += fields_non_required

    for field in fields:
        annotations[field.name] = field.type_
        if not field.required:
            kwdefaults[field.name] = field.default

    if as_method:
        codes = [f"def {bind_func_name}(self, *,"]
    else:
        codes = [f"def {bind_func_name}(*,"]

    # definition kwargs.
    for field in fields:
        if field.required:
            codes.append(f"  {field.name},")
        else:
            codes.append(f"  {field.name}=None,")

    codes.append("):")
    codes.append(f"  return {bind_model_name}(")

    # create instance
    for field in fields:
        codes.append(f"    {field.name}={field.name},")

    codes.append("  )")
    code = "\n".join(codes)
    return (
        code,
        bind_func_name,
        bind_model_name,
        annotations,
        tuple(defaults),
        kwdefaults,
    )


def generate_funnel(cls: Type[BaseModel], as_method=False):
    """
    pydantic BaseModelで定義した属性を引数とするコンストラクタ関数を作成する。
    """
    (
        code,
        bind_func_name,
        bind_model_name,
        annotations,
        defaults,
        kwdefaults,
    ) = convert_to_func_code_from_pydantic(cls, as_method)
    local_namespace = {bind_func_name: None, bind_model_name: cls}
    exec(code, local_namespace, local_namespace)
    func = local_namespace[bind_func_name]
    func.__annotations__ = annotations  # 引数に型を付与
    # func.__defaults__  # 位置引数のデフォルトを定義  # POSITIONAL_OR_KEYWORDの場合は、defaultsに定義される
    func.__kwdefaults__ = kwdefaults  # キーワード引数のデフォルト値
    return func


def generate_fastapi_funnel(cls: Type[BaseModel], as_method=False):
    func = generate_funnel(cls=cls, as_method=as_method)
    queries = convert_to_query_from_basemodel_fields(cls)
    # func.__defaults__  # 位置引数のデフォルトを定義  # POSITIONAL_ONLYかPOSITIONAL_OR_KEYWORDの場合は、defaultsに定義される
    func.__kwdefaults__ = queries
    return func


def generate_typer_funnel(cls: Type[BaseModel], as_method=False, options: dict = {}):
    func = generate_funnel(cls=cls, as_method=as_method)
    dic = detect_typer_incompatibles(func)
    queries = get_typer_options(cls, dic, **options)
    # func.__defaults__  # 位置引数のデフォルトを定義  # POSITIONAL_ONLYかPOSITIONAL_OR_KEYWORDの場合は、defaultsに定義される
    func.__kwdefaults__ = queries
    for k, v in dic.items():
        func.__annotations__[k] = v[0]  # typerに対応する型に変換する
    return func


def convert_to_query_from_basemodel_fields(cls: Type[BaseModel]) -> dict:
    from fastapi import Query
    from pydantic import Field

    result = {}

    for k, field in cls.__fields__.items():
        # field = cls.__fields__[k]
        if field.required:
            query = Query(..., alias=field.alias)
        else:
            if field.default_factory:
                raise Exception("動的な値の生成はドキュメント化できないため、使用できません。固定値にしてください。")
            query = Query(field.default, alias=field.alias)

        result[k] = query

    return result


def get_typer_options(cls: Type[BaseModel], incompatibles, **kwargs) -> dict:
    from typer import Option

    result = {}
    for k, field in cls.__fields__.items():
        if field.required:
            kwargs["help"] = (
                field.field_info.description if field.field_info.description else ""
            )
            default = ""  # defaultは省略不可
        else:
            default = field.default_factory if field.default_factory else field.default
            kwargs["help"] = (
                field.field_info.description if field.field_info.description else ""
            )

        if k in incompatibles:
            default = incompatibles[k][1]  # 0:type 1:default

        query = Option(default, **kwargs)

        # XXX: typerでエイリアスは使えない（多分）
        # TODO: pydanticのconst=Trueの場合は、値を指定する必要がないので除外する
        # TODO: __root__を定義したモデルをどう対応するべきか検討する必要がある

        result[k] = query

    return result


def detect_typer_incompatibles(func):
    # TODO: ConstrainedStrValueに対応させる
    # entrypoint: str = Field(min_length=1)
    # RuntimeError: Type not yet supported: <class 'rabbitmq.cli.ConstrainedStrValue'>

    change = {}
    for name, typ in func.__annotations__.items():
        if AnyAnalyzer(typ).is_literal():
            # change[name] = literal_to_enum(typ)
            change[name] = Converter.literal_to_enum(typ)

    for name, enum_ in change.items():
        if name in func.__kwdefaults__:
            change[name] = (enum_, enum_(func.__kwdefaults__[name]))
        else:
            raise Exception("位置orキーワード引数には対応していません。")

    return change
