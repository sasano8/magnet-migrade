from enum import Enum
from typing import Literal

from pydantic import validate_arguments

exchanges = Literal[
    "bitflyer",
    "zaif",
]


cryptowatch_currency_pair = Literal["btcjpy"]

zaif_currency_pair = Literal[
    "btc_jpy",
    "xem_jpy",
    "xem_btc",
    "cszaif_zaif",
    "csxem_xem",
    "zaif_btc",
    "mona_btc",
    "ncxc_btc",
    "cicc_btc",
    "eth_btc",
    "xcp_btc",
    "ncxc_jpy",
    "zaif_jpy",
    "erc20.cms_btc",
    "cscmsxem_mosaic.cms",
    "fscc_btc",
    "mosaic.cms_jpy",
    "xcp_jpy",
    "cseth_eth",
    "cscmseth_erc20.cms",
    "mona_jpy",
    "eth_jpy",
    "erc20.cms_jpy",
    "bch_jpy",
    "csbtc_btc",
    "jpyz_jpy",
    "cicc_jpy",
    "bch_btc",
    "fscc_jpy",
    "mosaic.cms_btc",
]


bitflyer_currency_pair = Literal[
    "BTC_JPY",
]


class CurrencyPair(Enum):
    btc_jpy = "btc_jpy"
    xem_jpy = "xem_jpy"
    xem_btc = "xem_btc"
    cszaif_zaif = "cszaif_zaif"
    csxem_xem = "csxem_xem"
    zaif_btc = "zaif_btc"
    mona_btc = "mona_btc"
    ncxc_btc = "ncxc_btc"
    cicc_btc = "cicc_btc"
    eth_btc = "eth_btc"
    xcp_btc = "xcp_btc"
    ncxc_jpy = "ncxc_jpy"
    zaif_jpy = "zaif_jpy"
    erc20__cms_btc = "erc20.cms_btc"
    cscmsxem_mosaic__cms = "cscmsxem_mosaic.cms"
    fscc_btc = "fscc_btc"
    mosaic__cms_jpy = "mosaic.cms_jpy"
    xcp_jpy = "xcp_jpy"
    cseth_eth = "cseth_eth"
    cscmseth_erc20__cms = "cscmseth_erc20.cms"
    mona_jpy = "mona_jpy"
    eth_jpy = "eth_jpy"
    erc20__cms_jpy = "erc20.cms_jpy"
    bch_jpy = "bch_jpy"
    csbtc_btc = "csbtc_btc"
    jpyz_jpy = "jpyz_jpy"
    cicc_jpy = "cicc_jpy"
    bch_btc = "bch_btc"
    fscc_jpy = "fscc_jpy"
    mosaic__cms_btc = "mosaic.cms_btc"


mapping_currency_pairs_cryptowatch_to_bitflyer = {
    # "btcjpy": "BTC_JPY",
    "btcjpy": "FX_BTC_JPY"
}


mapping_currency_pairs_cryptowatch_to_zaif = {"btcjpy": "btc_jpy"}


@validate_arguments
def convert_currency_pair_original(
    currency_pair: cryptowatch_currency_pair, dest_exchange: exchanges
) -> str:
    if dest_exchange == "bitflyer":
        return mapping_currency_pairs_cryptowatch_to_bitflyer[currency_pair]

    elif dest_exchange == "zaif":
        return mapping_currency_pairs_cryptowatch_to_zaif[currency_pair]

    else:
        raise ValueError(f"Unknown Exchange: {dest_exchange}")


class Exchange(Enum):
    ZAIF = "zaif"
    BITFLYER = "bitflyer"
