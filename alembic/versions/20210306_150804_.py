"""empty message

Revision ID: 20210306_150804
Revises: 20210306_082645
Create Date: 2021-03-06 15:08:04.528350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20210306_150804"
down_revision = "20210306_082645"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "trade_acount",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=False),
        sa.Column("market", sa.String(length=255), nullable=False),
        sa.Column("accounts", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("trade_acount")
    # ### end Alembic commands ###
