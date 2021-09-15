import aiohttp
import asyncio
import pandas


# another thing that could be cool is algo buying fat orderbook breaks

async def make_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def get_candles(symbol: str, interval: str):
    base = 'https://api1.binance.com'
    slug = f'/api/v3/klines'
    params = f'?symbol={symbol}&interval={interval}'
    return await make_request(base + slug + params)


async def get_symbols():
    base = 'https://api1.binance.com'
    slug = f'/api/v1/exchangeInfo'
    res = await make_request(base + slug)
    return res['symbols']


async def main():
    symbols = [i['symbol'] for i in await get_symbols())]
    candles = {}
    for symbol in symbols:
        candles[symbol] = await get_candles(symbol)


if __name__ == '__main__':
    asyncio.run(main())
    
