"""empty message

Revision ID: 20210329_230444
Revises: 20210329_190000
Create Date: 2021-03-29 23:04:44.214640

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20210329_230444"
down_revision = "20210329_190000"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "trade_profiles",
        sa.Column(
            "is_stop_reverse", sa.Boolean(), nullable=True, comment="ドテン売買でポジションを乗り換え"
        ),
    )
    op.execute("UPDATE trade_profiles SET is_stop_reverse = false")
    op.alter_column(
        "trade_profiles",
        sa.Column(
            "is_stop_reverse", sa.Boolean(), nullable=False, comment="ドテン売買でポジションを乗り換え"
        ),
    )
    op.alter_column(
        "trade_profiles",
        "description",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "trade_profiles",
        "description",
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
    )
    op.drop_column("trade_profiles", "is_stop_reverse")
    # ### end Alembic commands ###
