# standard type
bool = bool
int = int
float = float
str = str
bytes = bytes
list = list
tuple = tuple
dict = dict
set = set
frozenset = frozenset

# from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
)
from pathlib import Path
from typing import (
    AbstractSet,
    Any,
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
    Generator,
    Iterable,
    List,
    Literal,
    Mapping,
    NewType,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from uuid import UUID

from pydantic.color import Color
from pydantic.networks import (
    AnyHttpUrl,
    AnyUrl,
    EmailStr,
    HttpUrl,
    IPvAnyAddress,
    IPvAnyInterface,
    IPvAnyNetwork,
    NameEmail,
    PostgresDsn,
    RedisDsn,
    stricturl,
)
from pydantic.types import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    ByteSize,
    DirectoryPath,
    FilePath,
    Json,
    NegativeFloat,
    NegativeInt,
    PaymentCardBrand,
    PaymentCardNumber,
    PositiveFloat,
    PositiveInt,
    PyObject,
    SecretBytes,
    SecretStr,
    conbytes,
    condecimal,
    confloat,
    conint,
    conlist,
    constr,
)
