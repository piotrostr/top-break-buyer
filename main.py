import asyncio
import pandas as pd

from aiohttp import ClientSession

# another thing that could be cool is algo buying fat orderbook breaks

async def make_request(session: ClientSession, url: str):
    async with session.get(url) as response:
        return await response.json()


async def get_candles(session: ClientSession, symbol: str, interval: str):
    base = 'https://api1.binance.com'
    slug = f'/api/v3/klines'
    params = f'?symbol={symbol}&interval={interval}'
    return await make_request(session, base + slug + params)


async def get_symbols(session: ClientSession):
    base = 'https://api1.binance.com'
    slug = f'/api/v1/exchangeInfo'
    res = await make_request(session, base + slug)
    return res['symbols']


async def main():
    async with ClientSession() as session:
        symbols = [i['symbol'] for i in await get_symbols(session)]
        symbols = [symbol for symbol in symbols if 'USDT' in symbol]
        symbols = symbols[:2]
        tasks = []
        for symbol in symbols:
            task = asyncio.ensure_future(get_candles(session, symbol, '1h'))
            tasks.append(task)
        return (symbols, await asyncio.gather(*tasks))


if __name__ == '__main__':
    symbols, candles = asyncio.run(main())
    res = dict(list(zip(symbols, candles)))

