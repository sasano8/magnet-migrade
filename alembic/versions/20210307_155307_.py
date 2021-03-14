"""empty message

Revision ID: 20210307_155307
Revises: 20210306_212825
Create Date: 2021-03-07 15:53:07.493094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20210307_155307'
down_revision = '20210306_212825'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trade_virtual_account', 'trade_account_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trade_virtual_account', 'trade_account_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
