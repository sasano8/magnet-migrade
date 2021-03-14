import json
from typing import Any, List

from pydantic import BaseModel, create_model
from pydantic.fields import ModelField

"""
API仕様を定義するフォーマットとして、OpenApPIとJson Schemaが存在する。
これらは、近い互換性を持っているが非互換が存在するため、どちらを使うべきか検討しておいた方がよい。

OpenAPIは、Json Schemaを完全に読み込むことができ、かつ、Json Schemaのサブセットとして、拡張機能を提供することを目指している。（現時点では、完全な互換性ではない。）
Json SchemaはOpenAPIを考慮しない。
そのため、まずはJson Schemaを利用するのがいいだろう。
"""

# from genson import SchemaBuilder
# from datamodel_code_generator.parser.openapi import OpenAPIParser
# from datamodel_code_generator.parser.jsonschema import JsonSchemaParser


class JsonModel(BaseModel):
    __model_name: str = "Dummy"
    model: Any
    columns: List[ModelField]
    indent: int = 2
    require_default: bool = False
    set_default_from_json: bool = False

    class Config:
        arbitrary_types_allowed = True

    def output_pydantic_code(self):
        str_indent = "  "

        lines = [
            "from pydantic import BaseModel",
            f"class {self.__model_name}(BaseModel):",
        ]

        for field in self.columns:
            code = self.output_pydantic_field(field)
            lines.append(str_indent + code)

        sample = self.model.Config.schema_extra["example"]
        dumps = json.dumps(sample, ensure_ascii=False)
        # import collections
        # dic = collections.OrderedDict()

        if sample:
            lines.append("")
            lines.append(str_indent + "class Config:")
            lines.append(str_indent * 2 + "schema_extra = {")
            lines.append(str_indent * 3 + f'"example": {dumps}')  # orderded dictを考慮する
            lines.append(str_indent * 2 + "}")

        # class Config:
        #     schema_extra = {
        #         "example": {
        #             "pipeline_name": "postgres",
        #             "crawler_name": "scrape_google",
        #             "keyword": "山田太郎",
        #             "option_keywords": []
        #         }
        #     }

        return "\n".join(lines)

    def output_pydantic_field(self, field):
        if self.require_default:
            if field.type_ is str:
                default_value = f' = "{field.default}"'
            else:
                default_value = f" = {field.default}"
        else:
            default_value = ""

        required = True
        # required = field.required

        if required:
            return f"{field.name}: {field.type_.__name__}" + default_value
        else:
            return f"{field.name}: Optional[{field.type_.__name__}]" + default_value

    def output_sqlalchemy_code(self):
        str_indent = "  "
        decreative_base = "Base"

        lines = [
            f"class {self.__model_name}Table({decreative_base}):",
            str_indent + "id = Column(Integer, primary_key=True, index=True)",
        ]

        for field in self.columns:
            code = self.output_sqlalchemy_field(field)
            lines.append(str_indent + code)

        return "\n".join(lines)

    def output_sqlalchemy_field(self, field):
        sql_alchemy_type = self.map_sqlalcemy_type(field.type_)
        if field.type_ is str:
            return f'{field.name} = Column({sql_alchemy_type}, blank=True, nullable=False, server_default="")'
        elif field.type_ is int:
            return f"{field.name} = Column({sql_alchemy_type}, nullable=False, server_default=0)"
        elif field.type_ is float:
            return f"{field.name} = Column({sql_alchemy_type}, nullable=False, server_default=0)"
        elif field.type_ is bool:
            return f"{field.name} = Column({sql_alchemy_type}, nullable=False, server_default=False)"
        else:
            return "Undefine"

    def map_sqlalcemy_type(self, _type):
        if _type is str:
            return "String(1023)"
        elif _type is int:
            return "Ingeger"
        elif _type is float:
            return "Float"
        elif _type is bool:
            return "Bool"
        else:
            return "Undefine"


def dump_pydantic_code_from_json(
    __model_name: str,
    data,
    indent: int = 2,
    require_default: bool = False,
    set_default_from_json: bool = False,
):
    if isinstance(data, list):
        is_list = True
        if len(data):
            data = data[0]
        else:
            data = None

    else:
        is_list = False

    if isinstance(data, BaseModel):
        schema = data
        data = schema.dict()

    else:
        schema = create_model(__model_name, **data)

        class Config:
            schema_extra = {"example": data}

        schema.Config = Config

    # テスト
    fields = list(schema.__fields__.values())
    obj = JsonModel(__model_name=__model_name, model=schema, columns=fields)

    pydantic = obj.output_pydantic_code()
    sqlalchemy = obj.output_sqlalchemy_code()

    return "\n".join([pydantic, "", sqlalchemy])
