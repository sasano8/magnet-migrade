"""empty message

Revision ID: 20210318_075330
Revises: 20210317_233807
Create Date: 2021-03-18 07:53:30.477419

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20210318_075330'
down_revision = '20210317_233807'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trade_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=255), nullable=False),
    sa.Column('market', sa.String(length=255), nullable=False),
    sa.Column('product', sa.String(length=255), nullable=False),
    sa.Column('periods', sa.Integer(), nullable=False),
    sa.Column('analyzers', sa.JSON(), nullable=False),
    sa.Column('slippage', sa.DECIMAL(), nullable=True, comment='バックテストにおいては約定価格のブレを表現し、実際の取引ではショートサーキットのように動作します？？'),
    sa.Column('limit_rate', sa.DECIMAL(), nullable=True),
    sa.Column('stop_rate', sa.DECIMAL(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('trade_bots', sa.Column('close_cancel_order', sa.JSON(), nullable=True))
    op.add_column('trade_bots', sa.Column('close_finalized', sa.JSON(), nullable=True))
    op.add_column('trade_bots', sa.Column('close_order', sa.JSON(), nullable=True))
    op.add_column('trade_bots', sa.Column('entry_cancel_order', sa.JSON(), nullable=True))
    op.add_column('trade_bots', sa.Column('entry_finalized', sa.JSON(), nullable=True))
    op.add_column('trade_bots', sa.Column('entry_order', sa.JSON(), nullable=True))
    op.add_column('trade_bots', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('trade_bots', sa.Column('profile_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'trade_bots', ['profile_id'])
    op.create_foreign_key(None, 'trade_bots', 'trade_profiles', ['profile_id'], ['id'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.drop_column('trade_bots', 'api_data')
    op.drop_column('trade_bots', 'reason')
    op.drop_column('trade_bots', 'market')
    op.drop_column('trade_bots', 'periods')
    op.drop_column('trade_bots', 'slippage')
    op.drop_column('trade_bots', 'product')
    op.drop_column('trade_bots', 'limit_rate')
    op.drop_column('trade_bots', 'provider')
    op.drop_column('trade_bots', 'stop_rate')
    op.drop_column('trade_bots', 'analyzers')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('trade_bots', sa.Column('analyzers', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.add_column('trade_bots', sa.Column('stop_rate', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.add_column('trade_bots', sa.Column('provider', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('trade_bots', sa.Column('limit_rate', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.add_column('trade_bots', sa.Column('product', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('trade_bots', sa.Column('slippage', sa.NUMERIC(), autoincrement=False, nullable=True, comment='バックテストにおいては約定価格のブレを表現し、実際の取引ではショートサーキットのように動作します？？'))
    op.add_column('trade_bots', sa.Column('periods', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('trade_bots', sa.Column('market', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('trade_bots', sa.Column('reason', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('trade_bots', sa.Column('api_data', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'trade_bots', type_='foreignkey')
    op.drop_constraint(None, 'trade_bots', type_='unique')
    op.drop_column('trade_bots', 'profile_id')
    op.drop_column('trade_bots', 'is_active')
    op.drop_column('trade_bots', 'entry_order')
    op.drop_column('trade_bots', 'entry_finalized')
    op.drop_column('trade_bots', 'entry_cancel_order')
    op.drop_column('trade_bots', 'close_order')
    op.drop_column('trade_bots', 'close_finalized')
    op.drop_column('trade_bots', 'close_cancel_order')
    op.drop_table('trade_profiles')
    # ### end Alembic commands ###