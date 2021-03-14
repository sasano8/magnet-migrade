from typing import List

from fastapi import Depends

from pandemic import APIRouter

from ...commons import PagenationQuery
from ...database import Session, get_db
from . import models, schemas

router = APIRouter()

DummyService = models.Dummy.as_service()


class Dummy:
    @staticmethod
    @router.get("/")
    async def index(
        db: Session = Depends(get_db), *, q: PagenationQuery
    ) -> List[schemas.Dummy]:
        return DummyService.index(db, skip=q.skip, limit=q.limit)

    @staticmethod
    @router.post("/")
    async def create(
        db: Session = Depends(get_db),
        *,
        data: schemas.Dummy.prefab(suffix="Create", exclude={"id"})
    ) -> schemas.Dummy:
        return DummyService.create(db, **data.dict())

    @staticmethod
    @router.get("/{id}")
    async def get(db: Session = Depends(get_db), *, id: int) -> schemas.Dummy:
        return DummyService.get(db, id=id)

    @staticmethod
    @router.delete("/{id}/delete", status_code=200)
    async def delete(db: Session = Depends(get_db), *, id: int) -> int:
        return DummyService.delete(db, id=id)

    @staticmethod
    @router.patch("/{id}/patch")
    async def patch(
        db: Session = Depends(get_db),
        *,
        id: int,
        data: schemas.Dummy.prefab(suffix="Patch", optionals=...)
    ) -> schemas.Dummy:
        data = schemas.Dummy(**data.dict(exclude={"id"}), id=id)
        return DummyService.patch(db, **data.dict())

    @staticmethod
    @router.post("/{id}/copy")
    async def copy(db: Session = Depends(get_db), *, id: int) -> schemas.Dummy:
        return DummyService.duplicate(db, id=id)
