from enum import Enum
from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from ...commons import PagenationQuery, TemplateView, fastapi_funnel
from ...database import Session, get_db
from . import crud, models, schemas


class ResearchMenu(str, Enum):
    default = "default"
    carefully = "carefully"
    stock = "stock"


class Language(str, Enum):
    jp = "jp"
    en = "en"


router = InferringRouter()


@cbv(router)
class CaseNodeView(TemplateView[crud.Casenode]):
    db: Session = Depends(get_db)

    @property
    def rep(self) -> crud.Target:
        return super().rep

    @router.get("/case")
    @fastapi_funnel
    async def index(self, q: PagenationQuery) -> List[schemas.CaseNode]:
        return super().index(skip=q.skip, limit=q.limit)

    @router.post("/case")
    async def create(
        self, data: schemas.CaseNode.prefab("Create", exclude=["id"])
    ) -> schemas.CaseNode:
        return super().create(data=data)

    @router.get("/case/{id}")
    async def get(self, id: int) -> schemas.CaseNode:
        return super().get(id=id)

    @router.delete("/case/{id}/delete", status_code=200)
    async def delete(self, id: int) -> int:
        return super().delete(id=id)

    @router.patch("/case/{id}/patch")
    async def patch(
        self, id: int, data: schemas.CaseNode.prefab("Patch", optionals=...)
    ) -> schemas.CaseNode:
        return super().patch(id=id, data=data)

    @router.post("/case/{id}/copy")
    async def copy(self, id: int) -> schemas.CaseNode:
        return super().duplicate(id=id)


@cbv(router)
class TargetView(TemplateView[crud.Target]):
    db: Session = Depends(get_db)

    @property
    def rep(self) -> crud.Target:
        return super().rep

    @router.get("/target")
    @fastapi_funnel
    async def index(self, q: PagenationQuery) -> List[schemas.Target]:
        return super().index(skip=q.skip, limit=q.limit)

    @router.post("/target")
    async def create(
        self, data: schemas.Target.prefab("Create", exclude=["id"])
    ) -> schemas.Target:
        return super().create(data=data)

    @router.get("/target/{id}")
    async def get(self, id: int) -> schemas.Target:
        return super().get(id=id)

    @router.delete("/target/{id}/delete", status_code=200)
    async def delete(self, id: int) -> int:
        return super().delete(id=id)

    @router.patch("/target/{id}/patch")
    async def patch(
        self, id: int, data: schemas.Target.prefab("Patch", optionals=...)
    ) -> schemas.Target:
        return super().patch(data=data)

    @router.post("/target/{id}/copy")
    async def copy(self, id: int) -> schemas.Target:
        return super().duplicate(id=id)
