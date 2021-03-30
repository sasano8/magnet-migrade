"""empty message

Revision ID: 20210330_005835
Revises: 20210329_235206
Create Date: 2021-03-30 00:58:35.283175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20210330_005835'
down_revision = '20210329_235206'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trade_orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_stop_reverse', sa.Boolean(), nullable=False, comment='ドテン売買でポジションを乗り換え'),
    sa.Column('product_code', sa.String(length=255), nullable=True),
    sa.Column('entry_at', sa.DateTime(timezone=True), nullable=True, comment='成行前提でエントリー時に日時を確定させる'),
    sa.Column('entry_order', sa.JSON(), nullable=True, comment='エントリー注文。エントリーは成行で行われ、リミット・ストップ監視まで面倒を見る。'),
    sa.Column('entry_order_accepted', sa.JSON(), nullable=True),
    sa.Column('entry_order_finalized', sa.JSON(), nullable=True),
    sa.Column('entry_cancel_order', sa.JSON(), nullable=True, comment='リミット・ストップ監視を止めるためのキャンセル注文'),
    sa.Column('entry_cancel_order_accepted', sa.JSON(), nullable=True),
    sa.Column('entry_cancel_order_finalized', sa.JSON(), nullable=True),
    sa.Column('counter_at', sa.DateTime(timezone=True), nullable=True, comment='成行前提で反対売買時に日時を確定させる。リミット・ストップの場合は、APIによって日時が取れないので認識した日付を入力。'),
    sa.Column('counter_order', sa.JSON(), nullable=True, comment='残エントリーを決済するための反対売買注文'),
    sa.Column('counter_order_accepted', sa.JSON(), nullable=True),
    sa.Column('counter_order_finalized', sa.JSON(), nullable=True),
    sa.Column('finalized', sa.JSON(), nullable=True, comment='entryとcounterの結果をまとめる'),
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['trade_profiles.id'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('profile_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trade_orders')
    # ### end Alembic commands ###