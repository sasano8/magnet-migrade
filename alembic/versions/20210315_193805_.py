"""empty message

Revision ID: 20210315_193805
Revises: 20210315_151433
Create Date: 2021-03-15 19:38:05.486503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20210315_193805'
down_revision = '20210315_151433'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('etl_job_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted', sa.DateTime(timezone=True), nullable=False),
    sa.Column('inserted', sa.DateTime(timezone=True), nullable=False),
    sa.Column('errors', sa.JSON(), nullable=False),
    sa.Column('error_summary', sa.Text(), nullable=False),
    sa.Column('warning', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('__crypto_ohlc_daily', 't_cross',
               existing_type=sa.INTEGER(),
               comment='1=golden cross -1=dead cross 2021/3/15 t_sma_5 t_sma_25のクロスを検出',
               existing_comment='1=golden cross -1=dead cross',
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('__crypto_ohlc_daily', 't_cross',
               existing_type=sa.INTEGER(),
               comment='1=golden cross -1=dead cross',
               existing_comment='1=golden cross -1=dead cross 2021/3/15 t_sma_5 t_sma_25のクロスを検出',
               existing_nullable=False)
    op.drop_table('etl_job_results')
    # ### end Alembic commands ###