import aiohttp
from app.config import ALPHA_VANTAGE_API_KEY


async def fetch_data_from_api(symbol: str, session: aiohttp.ClientSession) -> dict:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()
