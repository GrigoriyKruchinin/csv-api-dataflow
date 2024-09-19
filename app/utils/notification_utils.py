from aiogram import Bot
from app.config import TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_API_TOKEN)


async def send_telegram_message(message: str):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
