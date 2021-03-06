"""empty message

Revision ID: 20210324_003847
Revises: 20210323_050840
Create Date: 2021-03-24 00:38:47.860728

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20210324_003847"
down_revision = "20210323_050840"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "trade_bots", sa.Column("product_code", sa.String(length=255), nullable=True)
    )
    op.execute("UPDATE trade_bots SET product_code = ''")
    op.alter_column(
        "trade_bots", sa.Column("product_code", sa.String(length=255), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("trade_bots", "product_code")
    # ### end Alembic commands ###
