"""empty message

Revision ID: 20210315_075349
Revises: 20210314_095815
Create Date: 2021-03-15 07:53:50.158530

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20210315_075349'
down_revision = '20210314_095815'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tradeorder')
    op.alter_column('users', 'full_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'full_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_table('tradeorder',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('description', sa.VARCHAR(length=1024), autoincrement=False, nullable=False),
    sa.Column('provider', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('market', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('product', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('order_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='apiが注文を受け付けた日付'),
    sa.Column('order_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True, comment='apiから発行される外部id'),
    sa.Column('bid_or_ask', sa.VARCHAR(length=255), autoincrement=False, nullable=True, comment='apiから発行される外部id'),
    sa.Column('kwargs', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('order_type', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('broker', sa.VARCHAR(length=1024), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='tradeorder_pkey')
    )
    # ### end Alembic commands ###