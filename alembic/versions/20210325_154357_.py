"""empty message

Revision ID: 20210325_154357
Revises: 20210324_225102
Create Date: 2021-03-25 15:43:58.213550

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20210325_154357"
down_revision = "20210324_225102"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "__crypto_ohlc_daily",
        sa.Column(
            "wb_cs", sa.DECIMAL(), nullable=True, comment="white black candle stick"
        ),
    )
    op.alter_column(
        "trade_logs",
        "fact_profit_rate",
        existing_type=sa.NUMERIC(),
        nullable=False,
        existing_comment="数量と手数料を含んだ実際の損益率",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "trade_logs",
        "fact_profit_rate",
        existing_type=sa.NUMERIC(),
        nullable=True,
        existing_comment="数量と手数料を含んだ実際の損益率",
    )
    op.drop_column("__crypto_ohlc_daily", "wb_cs")
    # ### end Alembic commands ###