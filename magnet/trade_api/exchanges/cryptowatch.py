import datetime
import json
from typing import Dict, List, Mapping, Tuple

import httpx
from pydantic import BaseModel, parse_obj_as

from libs import create_params, decorators


class Allowance(BaseModel):
    cost: float
    remaining: float
    upgrade: str


class Pairs(BaseModel):
    id: int
    symbol: str
    base: dict
    quote: dict
    route: str


class Ohlc(BaseModel):
    close_time: datetime.datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    quote_volume: float


# @decorators.Instantiate
class CryptowatchAPI:
    last_allowance: Allowance = Allowance(cost=0, remaining=1000000, upgrade="")

    async def get_pairs(self) -> List[Pairs]:
        url = "https://api.cryptowat.ch/pairs"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        try:
            response.raise_for_status()
        except httpx._exceptions.HTTPError as err:
            raise err

        dic = json.loads(response.text)
        result = parse_obj_as(List[Pairs], dic["result"])
        return result

    async def list_ohlc(
        self,
        market: str = "bitflyer",
        product: str = "btcjpy",
        periods: int = 60 * 60 * 24,
        after: datetime.datetime = datetime.datetime(2010, 1, 1),
    ) -> List[Ohlc]:
        after_ = int(after.timestamp())
        url = f"https://api.cryptowat.ch/markets/{market}/{product}/ohlc?periods={periods}&after={after_}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        try:
            response.raise_for_status()
        except httpx._exceptions.HTTPError as err:
            raise err

        result = json.loads(response.text)
        self.last_allowance = Allowance(**result["allowance"])
        arr = result["result"][str(periods)]

        return list(
            map(
                lambda item: Ohlc(
                    close_time=datetime.datetime.fromtimestamp(item[0]),
                    open_price=item[1],
                    high_price=item[2],
                    low_price=item[3],
                    close_price=item[4],
                    volume=item[5],
                    quote_volume=item[6],
                ),
                arr,
            )
        )
