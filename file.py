import platform
from datetime import datetime, timedelta
import logging

import aiohttp
import asyncio
from enum import Enum

class CurrenciesEnum(Enum):
    EUR = 'EUR'
    USD = 'USD'

async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None

async def get_exchange(currency_code: CurrenciesEnum, days):
    today = datetime.now()
    exchange_rates = []

    for day in range(days):
        data_need = (today - timedelta(days=day)).strftime('%d.%m.%Y')
        result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={data_need}')
        
        if result:
            rates = result.get("exchangeRate")
            exc = [rate for rate in rates if rate["currency"] == currency_code.value]

            if exc:
                exchange_rates.append({data_need: {currency_code.name: {
                    'sale': exc[0]['saleRate'],
                    'purchase': exc[0]['purchaseRate']
                }}})

    return exchange_rates

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    days = int(input('Enter the number of days: '))

    if days <= 0:
        print("Invalid number of days.")
    else:
        currency_code = CurrenciesEnum(input('Currency code (EUR/USD): '))
        result = asyncio.run(get_exchange(currency_code, days))
        print(json.dumps(result, indent=2))
