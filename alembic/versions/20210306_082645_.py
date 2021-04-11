"""empty message

Revision ID: 20210306_082645
Revises: 20210212_004222
Create Date: 2021-03-06 08:26:45.187275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20210306_082645"
down_revision = "20210212_004222"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "__crypto_ohlc_daily", sa.Column("start_time", sa.Date(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("__crypto_ohlc_daily", "start_time")
    # ### end Alembic commands ###
