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


async def get_close_to_top():
    # this is pretty stupid, as 'close to top' assets might not be trending
    out = []
    symbols, all_candles = await get_data()
    for symbol, candles in zip(symbols, all_candles):
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


async def get_hot():
    # basically if based on the 200 volume, last 5 mins volume is greater  
    # and the one minute trades is greater than the average of the 200
    # and the change on the one minute is positive
    # return the asset
    out = []
    symbols, all_candles = await get_data()
    for symbol, candles in zip(symbols, all_candles):

        # data
        candles['volume'] = candles['volume'].astype(np.float64)
        mean_volume = candles['volume'].mean()
        recent_volume = candles['volume'].iloc[-5:].mean()
        last_candle = candles.iloc[-1]
        last_open = float(last_candle['open'])
        last_price = float(last_candle['close'])
        volume_last = last_candle['volume']
        volume_second_last = candles.iloc[-2]['volume']
        volume_third_last = candles.iloc[-3]['volume']
        volume_fourth_last = candles.iloc[-4]['volume']

        # conditions
        volume_is_greater = recent_volume > mean_volume * 2
        last_candle_is_green = last_open < last_price
        volume_is_increasing = (
            # volume_fourth_last 
            volume_third_last
            < volume_second_last
            < volume_last
        )
        if (
            volume_is_greater and 
            volume_is_increasing and 
            last_candle_is_green
        ):
            print(symbol)
            out.append(symbol)
    return out

if __name__ == '__main__':
    # TODO
    # backtest 🥺
    import time
    while True:
        out = asyncio.run(get_hot())
        time.sleep(61)

