"""empty message

Revision ID: 20210315_150751
Revises: 20210315_075349
Create Date: 2021-03-15 15:07:51.920783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20210315_150751"
down_revision = "20210315_075349"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "__crypto_ohlc_daily", sa.Column("optn_time", sa.Date(), nullable=True)
    )
    op.drop_column("__crypto_ohlc_daily", "start_time")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "__crypto_ohlc_daily",
        sa.Column("start_time", sa.DATE(), autoincrement=False, nullable=True),
    )
    op.drop_column("__crypto_ohlc_daily", "optn_time")
    # ### end Alembic commands ###
