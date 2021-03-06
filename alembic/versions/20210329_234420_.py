"""empty message

Revision ID: 20210329_234420
Revises: 20210329_230444
Create Date: 2021-03-29 23:44:21.166185

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20210329_234420"
down_revision = "20210329_230444"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "trade_bots",
        sa.Column(
            "is_stop_reverse", sa.Boolean(), nullable=True, comment="ドテン売買でポジションを乗り換え"
        ),
    )
    op.execute("update trade_bots set is_stop_reverse = false")
    op.alter_column(
        "trade_profiles",
        "is_stop_reverse",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_comment="ドテン売買でポジションを乗り換え",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "trade_profiles",
        "is_stop_reverse",
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_comment="ドテン売買でポジションを乗り換え",
    )
    op.drop_column("trade_bots", "is_stop_reverse")
    # ### end Alembic commands ###
