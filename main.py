import asyncio
import pandas as pd
import numpy as np
import talib

from aiohttp import ClientSession

# another thing that could be cool is algo buying fat orderbook breaks

async def make_request(session: ClientSession, url: str):
    async with session.get(url) as response:
        return await response.json()


async def get_candles(session: ClientSession, 
                      symbol: str, 
                      interval: str) -> pd.DataFrame:
    base = 'https://api1.binance.com'
    slug = f'/api/v3/klines'
    params = f'?symbol={symbol}&interval={interval}'
    res = await make_request(session, base + slug + params)
    df = pd.DataFrame(res)
    df = df[[0, 1, 2, 3, 4]]
    df.columns = ['t', 'o', 'h', 'l', 'c']
    return df


async def get_symbols(session: ClientSession):
    base = 'https://api1.binance.com'
    slug = f'/api/v1/exchangeInfo'
    res = await make_request(session, base + slug)
    return res['symbols']


async def get_data():
    async with ClientSession() as session:
        symbols = [i['symbol'] for i in await get_symbols(session)]
        symbols = [symbol for symbol in symbols if 'USDT' in symbol]
        tasks = []
        for symbol in symbols:
            task = asyncio.ensure_future(get_candles(session, symbol, '15m'))
            tasks.append(task)
        return (symbols, await asyncio.gather(*tasks))


if __name__ == '__main__':
    out = []
    symbols, _candles = asyncio.run(get_data())
    for symbol, candles in zip(symbols, _candles):
        candles = candles.astype(np.float64)
        current_price = candles['c'].iloc[-1] 
        high = max(candles['h'])
        # and also add condition that the volume is increasing
        atr_df = talib.ATR(candles['h'], candles['l'], candles['c'], 14)
        atr = atr_df.iloc[-1]
        if current_price > high:
            if high + atr > current_price:
                print(symbol)
                out.append(candles)
        else:
            if current_price + atr > high:
                print(symbol)
                out.append(candles)

