from libs.fastapi import GenericRepository

from . import models


class Casenode(GenericRepository[models.CaseNode]):
    pass


class Target(GenericRepository[models.Target]):
    pass
