from dotenv import load_dotenv
import os

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
