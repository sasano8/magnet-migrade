"""empty message

Revision ID: 20210329_190000
Revises: 20210329_185416
Create Date: 2021-03-29 19:00:00.565588

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20210329_190000"
down_revision = "20210329_185416"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "trade_profiles", sa.Column("description", sa.String(length=255), nullable=True)
    )
    op.execute("update trade_profiles set description = ''")
    op.alter_column(
        "trade_profiles",
        sa.Column("description", sa.String(length=255), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("trade_profiles", "description")
    # ### end Alembic commands ###
