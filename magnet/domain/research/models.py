import sqlalchemy as sa

from magnet.database import Base


# TODO: ツリー構造を実現したい
# https://kite.com/blog/python/sqlalchemy/
class CaseNode(Base):  # ノードの情報
    __tablename__ = "case_node"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=False)
    is_system = sa.Column(sa.Boolean, default=False, nullable=False)  # ルートのみに利用する想定
    description = sa.Column(sa.String(255), nullable=False)


class Target(Base):  # ノードの情報
    __tablename__ = "target"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=False)
    node_id = sa.Column(sa.Integer, sa.ForeignKey("case_node.id"))
