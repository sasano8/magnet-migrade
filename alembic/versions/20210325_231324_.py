"""empty message

Revision ID: 20210325_231324
Revises: 20210325_154357
Create Date: 2021-03-25 23:13:24.548984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20210325_231324'
down_revision = '20210325_154357'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('__crypto_ohlc_daily', sa.Column('t_rsi_14', sa.DECIMAL(), nullable=True))
    op.alter_column('__crypto_ohlc_daily', 'wb_cs',
               existing_type=sa.NUMERIC(),
               nullable=False,
               existing_comment='white black candle stick')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('__crypto_ohlc_daily', 'wb_cs',
               existing_type=sa.NUMERIC(),
               nullable=True,
               existing_comment='white black candle stick')
    op.drop_column('__crypto_ohlc_daily', 't_rsi_14')
    # ### end Alembic commands ###
