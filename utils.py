import aiohttp
import pandas as pd
from aiogram import Bot

from config import ALPHA_VANTAGE_API_KEY, TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_API_TOKEN)


async def fetch_data_from_api(symbol: str, session: aiohttp.ClientSession) -> dict:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


def extract_ticker(row: pd.Series) -> str:
    for value in row:
        value_str = str(value)
        if 2 <= len(value_str) <= 6 and value_str.isupper():
            return value_str
    return None


async def send_telegram_message(message: str):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
