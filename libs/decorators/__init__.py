from libs.decorators.abstract import FuncDecorator
from libs.decorators.impl import Instantiate  # MapJsonAsync
from libs.decorators.impl import Decode, Hook, MapDict, MapJson, PrintLog, Tag
from libs.decorators.repository import Repoisotry


class Decorator(FuncDecorator):
    def wrapper(self, func, *args, **kwargs):
        return
