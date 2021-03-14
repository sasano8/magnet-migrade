import sqlalchemy as sa

from framework import DateTimeAware


# SQLAlchemy
class TimeStampMixin:
    """ Timestamping mixin"""

    created_at = sa.Column(sa.DateTime(timezone=True), default=DateTimeAware.utcnow)
    created_at._creation_order = 9998  # 列作成の優先順位
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=DateTimeAware.utcnow,
    )
    updated_at._creation_order = 9998  # 列作成の優先順位

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = DateTimeAware.utcnow()

    @classmethod
    def __declare_last__(cls):
        sa.event.listen(cls, "before_update", cls._updated_at)
