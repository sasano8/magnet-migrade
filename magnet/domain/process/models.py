from __future__ import annotations

import sqlalchemy as sa

from ...database import Base, Session

# class Process(Base):
#     __tablename__ = "trade_detector"

#     id = sa.Column(sa.Integer, primary_key=True)
#     pid = sa.Column(sa.Integer, nullable=False)
#     is_system = sa.Column(sa.Boolean, nullable=False, default=False)
#     is_auto_start = sa.Column(sa.Boolean, nullable=False, default=False)
#     is_running = sa.Column(sa.Boolean, nullable=False, default=False)
#     command = sa.Column(sa.String, nullable=False, default=False)
#     state = sa.Column(sa.JSON, nullable=False, default={})
#     host = sa.Column(sa.String(255), nullable=False)
#     description = sa.Column(sa.String(1023), nullable=False)
