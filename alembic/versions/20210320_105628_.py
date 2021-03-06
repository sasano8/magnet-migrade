"""empty message

Revision ID: 20210320_105628
Revises: 20210318_081336
Create Date: 2021-03-20 10:56:28.384181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20210320_105628"
down_revision = "20210318_081336"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "trade_bots", sa.Column("close_order_finalized", sa.JSON(), nullable=True)
    )
    op.add_column(
        "trade_bots", sa.Column("entry_order_finalized", sa.JSON(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("trade_bots", "entry_order_finalized")
    op.drop_column("trade_bots", "close_order_finalized")
    # ### end Alembic commands ###
