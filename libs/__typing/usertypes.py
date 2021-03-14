# TODO: 使ってないなら消す

import itertools
from typing import Iterable, Optional

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.fields import ModelField


class Model(BaseModel):
    infinite: Iterable[int]

    # はじめの要素を取り出し検証して、イテレータを元に戻す
    @validator("infinite")
    # You don't need to add the "ModelField", but it will help your
    # editor give you completion and catch errors
    def infinite_first_int(cls: BaseModel, iterable, field: ModelField):
        first_value = next(iterable)
        if field.sub_fields:
            # The Iterable had a parameter type, in this case it's int
            # We use it to validate the first value
            sub_field = field.sub_fields[0]
            v, error = sub_field.validate(first_value, {}, loc="first_value")
            if error:
                raise ValidationError([error], cls)
        # This creates a new generator that returns the first value and then
        # the rest of the values from the (already started) iterable
        return itertools.chain([first_value], iterable)


# class PrimaryKey(Optional):
#     pass
#
#
# @table("mytable")
# class MyIdea1(BaseModel):
#     id: PrimaryKey  # wrap or create  Union[POST, PUT, DELETE, PATCH, ATTRIBUTE]
#
#     id: int = None
#     name: str = ""
#
#
# obj = MyIdea1()
# value = obj.id
