import asyncio
import argparse
import aiohttp
import json
from aiofiles import open as aio_open
from aiopath import AsyncPath

class CurrencyExchange:
    def __init__(self):
        self.api_url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
        self.supported_currencies = ['USD', 'EUR']
        self.days_limit = 10

    async def fetch_exchange_rate(self, date):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url + date) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data for date: {date}")

                data = await response.json()

                exchange_rates = {}
                for currency in self.supported_currencies:
                    rate = {
                        'sale': data['exchangeRate'][currency]['saleRate'],
                        'purchase': data['exchangeRate'][currency]['purchaseRate']
                    }
                    exchange_rates[currency] = rate

                return exchange_rates

    async def get_exchange_rates(self, days):
        today = await self.fetch_exchange_rate('')
        exchange_rates = []

        for day in range(days):
            date = today['date']
            rates = await self.fetch_exchange_rate(date)
            exchange_rates.append({date: rates})
            today = await self.fetch_exchange_rate(today['previousDate'])

        return exchange_rates

    async def save_exchange_rates_to_file(self, exchange_rates, filename):
        async with aio_open(filename, 'w') as file:
            await file.write(json.dumps(exchange_rates, indent=2))

    async def load_exchange_rates_from_file(self, filename):
        async with aio_open(filename, 'r') as file:
            return json.loads(await file.read())

    async def exchange(self, days, output_file=None):
        if days > self.days_limit:
            raise ValueError(f"Maximum allowed days is {self.days_limit}")

        exchange_rates = await self.get_exchange_rates(days)

        if output_file:
            await self.save_exchange_rates_to_file(exchange_rates, output_file)
        return exchange_rates

async def main():
    parser = argparse.ArgumentParser(description='Currency Exchange Utility')
    parser.add_argument('days', type=int, help='Number of days to retrieve exchange rates for')
    parser.add_argument('--output', '-o', help='Output file to save exchange rates')
    args = parser.parse_args()

    currency_exchange = CurrencyExchange()
    exchange_rates = await currency_exchange.exchange(args.days, args.output)

    print(json.dumps(exchange_rates, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
