from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import delete, update
from sqlalchemy.orm import Session

Base = declarative_base()


class User(Base):
    pass

    async def create(self, db: Session):
        db.add(self)
        await db.flush()

    async def upsert(self, db: Session):
        pass

    async def update(self, db: Session, **kwargs):
        q = update(self.__class__).where(self.__class__.id == self.id)
        q = q.values(**kwargs).execution_options(synchronize_session="fetch")
        result = await db.execute(q).one()
        await db.refresh(self)

    async def delete(self, db: Session):
        q = delete(self.__class__).where(self.__class__.id == self.id)
        await db.execute(q)


User(name="").create(db)
