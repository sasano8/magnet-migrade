"""empty message

Revision ID: 20210330_123602
Revises: 20210330_105838
Create Date: 2021-03-30 12:36:02.509213

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20210330_123602'
down_revision = '20210330_105838'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crypto_pairs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=255), nullable=False),
    sa.Column('symbol', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('symbol')
    )
    op.create_table('dummies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False, comment='ユニークな名前列です。テスト等で、データをルックアップするのに利用ください。'),
    sa.Column('date_naive', sa.DateTime(), nullable=True, comment='awareな日付を登録しても、timezoneは保持されません。データベースの設定に依存しますが、本アプリケーションは現地時間からutc時間へ変換が行われます。'),
    sa.Column('date_aware', sa.DateTime(timezone=True), nullable=True, comment='timezoneを保持します。オフセットのみ保持し、timezone名は保持しません。'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    comment='検証用に使うテーブルです。sqlalchemyの挙動確認テストでのみ使用してしています。'
    )
    op.create_table('topics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('referer', sa.String(length=1023), nullable=True),
    sa.Column('url', sa.String(length=1023), nullable=True),
    sa.Column('url_cache', sa.String(length=1023), nullable=True),
    sa.Column('title', sa.String(length=1023), nullable=True),
    sa.Column('summary', sa.String(length=1023), nullable=True),
    sa.Column('memo', sa.String(length=1023), nullable=False),
    sa.Column('detail', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('__crypto_pairs')
    op.drop_table('crypto_trade_results')
    op.drop_table('__topic')
    op.drop_table('dummy')
    op.drop_index('uix_query', table_name='__crypto_ohlc_daily')
    op.drop_table('__crypto_ohlc_daily')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('__crypto_ohlc_daily',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('provider', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('market', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('product', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('periods', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('close_time', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('open_price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('high_price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('low_price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('close_price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('volume', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('quote_volume', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_sma_5', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_sma_10', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_sma_15', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_sma_20', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_sma_25', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_sma_30', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_sma_200', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('t_cross', sa.INTEGER(), autoincrement=False, nullable=False, comment='1=golden cross -1=dead cross 2021/3/15 t_sma_5 t_sma_25のクロスを検出'),
    sa.Column('open_time', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('wb_cs', sa.NUMERIC(), autoincrement=False, nullable=False, comment='white black candle stick'),
    sa.Column('t_rsi_14', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('wb_cs_rate', sa.NUMERIC(), autoincrement=False, nullable=False, comment='white black candle stick'),
    sa.Column('t_sma_rate', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='__crypto_ohlc_daily_pkey'),
    sa.UniqueConstraint('provider', 'market', 'product', 'periods', 'close_time', name='__crypto_ohlc_daily_provider_market_product_periods_close_t_key'),
    comment='外部データソースから取得したチャート'
    )
    op.create_index('uix_query', '__crypto_ohlc_daily', ['provider', 'market', 'product', 'periods'], unique=False)
    op.create_table('dummy',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False, comment='ユニークな名前列です。テスト等で、データをルックアップするのに利用ください。'),
    sa.Column('date_naive', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='awareな日付を登録しても、timezoneは保持されません。データベースの設定に依存しますが、本アプリケーションは現地時間からutc時間へ変換が行われます。'),
    sa.Column('date_aware', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True, comment='timezoneを保持します。オフセットのみ保持し、timezone名は保持しません。'),
    sa.PrimaryKeyConstraint('id', name='dummy_pkey'),
    sa.UniqueConstraint('name', name='dummy_name_key'),
    comment='検証用に使うテーブルです。sqlalchemyの挙動確認テストでのみ使用してしています。'
    )
    op.create_table('__topic',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('referer', sa.VARCHAR(length=1023), autoincrement=False, nullable=True),
    sa.Column('url', sa.VARCHAR(length=1023), autoincrement=False, nullable=True),
    sa.Column('url_cache', sa.VARCHAR(length=1023), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=1023), autoincrement=False, nullable=True),
    sa.Column('summary', sa.VARCHAR(length=1023), autoincrement=False, nullable=True),
    sa.Column('memo', sa.VARCHAR(length=1023), autoincrement=False, nullable=False),
    sa.Column('detail', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='__topic_pkey')
    )
    op.create_table('crypto_trade_results',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('provider', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('market', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('product', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('periods', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('size', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('ask_or_bid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('entry_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('entry_close_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('entry_side', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('entry_price', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('entry_commission', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('entry_reason', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('settle_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('settle_close_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('settle_side', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('settle_price', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('settle_commission', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('settle_reason', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('job_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('job_version', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('is_back_test', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('close_date_interval', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('diff_profit', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('diff_profit_rate', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('fact_profit', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='crypto_trade_results_pkey')
    )
    op.create_table('__crypto_pairs',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('provider', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('symbol', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='__crypto_pairs_pkey'),
    sa.UniqueConstraint('symbol', name='__crypto_pairs_symbol_key')
    )
    op.drop_table('topics')
    op.drop_table('dummies')
    op.drop_table('crypto_pairs')
    # ### end Alembic commands ###
