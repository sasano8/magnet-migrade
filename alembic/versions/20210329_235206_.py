"""empty message

Revision ID: 20210329_235206
Revises: 20210329_234420
Create Date: 2021-03-29 23:52:06.869126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20210329_235206"
down_revision = "20210329_234420"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "trade_bots",
        "is_stop_reverse",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_comment="ドテン売買でポジションを乗り換え",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "trade_bots",
        "is_stop_reverse",
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_comment="ドテン売買でポジションを乗り換え",
    )
    # ### end Alembic commands ###
