import asyncio
import pandas as pd
import numpy as np
import talib

from aiohttp import ClientSession


async def make_request(session: ClientSession, url: str):
    async with session.get(url) as response:
        return await response.json()


async def get_candles(session: ClientSession, 
                      symbol: str, 
                      interval: str) -> pd.DataFrame:
    base = 'https://api1.binance.com'
    slug = '/api/v3/klines'
    params = f'?symbol={symbol}&interval={interval}'
    res = await make_request(session, base + slug + params)
    df = pd.DataFrame(res)
    df.columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'number_of_trades', 
        'taker_buy_volume', 'taker_buy_quote_volume', '_'
    ]
    return df


async def get_recent_trades(symbol: str):
    base = 'https://api1.binance.com'
    slug = '/api/v3/aggTrades'
    params = f'?symbol={symbol}'
    res = await make_request(session, base + slug + params)
    return res


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


async def main():
    # this is pretty stupid, as 'close to top' assets might not be trending
    out = []
    symbols, _candles = await get_data()
    for symbol, candles in zip(symbols, _candles):
        candles = candles.astype(np.float64)
        current_price = candles['close'].iloc[-1] 
        high = max(candles['high'])
        atr_df = talib.ATR(
            candles['high'], 
            candles['low'], 
            candles['close'], 
            14
        )
        atr = atr_df.iloc[-1]
        if current_price > high:
            if high + atr > current_price:
                print(symbol)
                out.append(candles)
        else:
            if current_price + atr > high:
                print(symbol)
                out.append(candles)


if __name__ == '__main__':
    # TODO
    # and also add condition that the volume is increasing
    # say if this 100 candles > previous 100 candles volume profile or sth
    # another thing that could be cool is algo buying fat orderbook breaks
    # and the top has to be in a given distance from the current rally
    # backtest 🥺

    async def func(symbol: str, interval: str):
        async with ClientSession() as session:
            candles = await get_candles(session, symbol, interval)
        return candles

    df = asyncio.run(func('BTCUSDT', '1m'))

