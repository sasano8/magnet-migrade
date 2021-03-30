import sqlalchemy as sa

from ...database import Base


class Dummy(Base):
    """検証用に使うテーブルです。sqlalchemyの挙動確認テストでのみ使用してしています。"""

    # __tablename__ = "dummy"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(
        sa.String(255),
        nullable=False,
        unique=True,
        comment="ユニークな名前列です。テスト等で、データをルックアップするのに利用ください。",
    )
    date_naive = sa.Column(
        sa.DateTime,
        nullable=True,
        comment="awareな日付を登録しても、timezoneは保持されません。データベースの設定に依存しますが、本アプリケーションは現地時間からutc時間へ変換が行われます。",
    )
    date_aware = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="timezoneを保持します。オフセットのみ保持し、timezone名は保持しません。",
    )

    # __table_args__ = {"comment": "検証用に使うテーブルです。sqlalchemyの挙動確認テストでのみ使用してしています。"}
