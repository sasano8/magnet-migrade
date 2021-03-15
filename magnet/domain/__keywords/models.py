from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ...database import Base


class Keywords(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True)
    category_name = Column(String, unique=True, index=True)
    tag = Column(String, index=True)
    keywords: Column(JSON, nullable=False, default=[])
    max_size = Column(Integer)
