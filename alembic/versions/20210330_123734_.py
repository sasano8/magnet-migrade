"""empty message

Revision ID: 20210330_123734
Revises: 20210330_123602
Create Date: 2021-03-30 12:37:34.288146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20210330_123734'
down_revision = '20210330_123602'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crypto_ohlcs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=255), nullable=False),
    sa.Column('market', sa.String(length=255), nullable=False),
    sa.Column('product', sa.String(length=255), nullable=False),
    sa.Column('periods', sa.Integer(), nullable=False),
    sa.Column('open_time', sa.Date(), nullable=True),
    sa.Column('close_time', sa.Date(), nullable=False),
    sa.Column('open_price', sa.Float(), nullable=False),
    sa.Column('high_price', sa.Float(), nullable=False),
    sa.Column('low_price', sa.Float(), nullable=False),
    sa.Column('close_price', sa.Float(), nullable=False),
    sa.Column('volume', sa.Float(), nullable=False),
    sa.Column('quote_volume', sa.Float(), nullable=False),
    sa.Column('wb_cs', sa.DECIMAL(), nullable=False, comment='white black candle stick'),
    sa.Column('wb_cs_rate', sa.DECIMAL(), nullable=False, comment='white black candle stick'),
    sa.Column('t_sma_5', sa.Float(), nullable=False),
    sa.Column('t_sma_10', sa.Float(), nullable=False),
    sa.Column('t_sma_15', sa.Float(), nullable=False),
    sa.Column('t_sma_20', sa.Float(), nullable=False),
    sa.Column('t_sma_25', sa.Float(), nullable=False),
    sa.Column('t_sma_30', sa.Float(), nullable=False),
    sa.Column('t_sma_200', sa.Float(), nullable=False),
    sa.Column('t_sma_rate', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('t_cross', sa.Integer(), nullable=False, comment='1=golden cross -1=dead cross 2021/3/15 t_sma_5 t_sma_25のクロスを検出'),
    sa.Column('t_rsi_14', sa.DECIMAL(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider', 'market', 'product', 'periods', 'close_time'),
    comment='外部データソースから取得したチャート'
    )
    op.create_index('uix_query', 'crypto_ohlcs', ['provider', 'market', 'product', 'periods'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('uix_query', table_name='crypto_ohlcs')
    op.drop_table('crypto_ohlcs')
    # ### end Alembic commands ###
