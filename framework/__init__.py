from inspect import _empty as undefined  # type: ignore
from typing import Any

from framework.analyzers import AnyAnalyzer

from .types import DateTimeAware
from .utils.linq import Linq, MiniDB
from .utils.udict import MappingDict as MappingDict
from .utils.udict import UndefinedDict as udict
