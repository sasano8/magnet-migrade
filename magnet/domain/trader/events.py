from framework import Linq

from ...database import get_db
from . import crud, models, schemas, views


async def upsert_default_trade_detector(db, /):
    rep = crud.TradeDetector(db=db)
    data = Linq([schemas.TradeScript])


async def upsert_default_data(db, /):
    default_profiles = Linq(
        [
            schemas.TradeProfile(
                id=1,
                name="ゴールデンクロス・デッドクロス売買",
                description="単純移動平均線5 25から算出したクロスサイン時にドテン売買を行う。",
                provider="cryptowatch",
                market="bitflyer",
                product="btcjpy",
                periods=60 * 60 * 24,
                cron="",
                broker="bitflyer",
                bet_strategy="flat",
                detector_name="detect_t_cross",
                job_type="backtest",
                order_logic=schemas.OrderLogic(
                    description="資産の20%投資。利確ロスカットなし。",
                    wallet="all",
                    allocation_rate=0.7,
                    min_unit=0.01,
                    ask_limit_rate=None,
                    ask_loss_rate=None,
                    bid_limit_rate=None,
                    bid_loss_rate=None,
                ),
            ),
            schemas.TradeProfile(
                id=2,
                name="ゴールデンクロス・デッドクロストレンド売買　騙しレンジ対応",
                description="ゴールデンクロス・デッドクロストレンド売買逆転である騙しやレンジ相場で利益を上げる",
                provider="cryptowatch",
                market="bitflyer",
                product="btcjpy",
                periods=60 * 60 * 24,
                cron="",
                broker="bitflyer",
                bet_strategy="flat",
                detector_name="detect_t_cross_invert",
                job_type="backtest",
                order_logic=schemas.OrderLogic(
                    description="利確ロスカットを設ける",
                    wallet="all",
                    allocation_rate=0.7,
                    min_unit=0.01,
                    ask_limit_rate=1.14,
                    ask_loss_rate=0.95,
                    bid_limit_rate=1.14,
                    bid_loss_rate=0.95,
                ),
            ),
        ]
    )

    rep = models.TradeProfile.as_rep()
    count, succeeded, exceptions = default_profiles.dispatch(
        lambda x: rep.upsert(db, **x.dict())
    )
    if exceptions:
        msg = "\n".join(str(x) for x in exceptions)
        raise Exception(msg)

    return {
        "inserted": 0,
        "deleted": 0,
        "upserted": succeeded,
        "errors": exceptions,
    }


@views.router.on_event("startup")
async def run_upsert_default_data():
    # fastapiのイベントは、Dependsできない
    for db in get_db():
        result = await upsert_default_data(db)
    return result
