import os
import sys
import json
import asyncio
from datetime import timedelta

import aiohttp
import aiofiles

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
import pandas as pd

from app.utils.api_utils import (
    fetch_data_from_api,
)
from app.utils.data_utils import extract_ticker
from app.utils.notification_utils import send_telegram_message

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


# Задача для загрузки данных из CSV
@task(
    retries=3,
    retry_delay_seconds=10,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
async def load_data_from_csv(file_path: str) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"Loading data from {file_path}")
    return pd.read_csv(file_path, sep=";")


# Задача для получения данных из API по тикеру
@task(retries=3, retry_delay_seconds=10)
async def fetch_api_data(symbol: str) -> dict:
    logger = get_run_logger()
    logger.info(f"Fetching data for {symbol}")
    async with aiohttp.ClientSession() as session:
        api_data = await fetch_data_from_api(
            symbol, session
        )
    return api_data


# Задача для сохранения данных в JSON
@task
async def save_to_json(data: dict, output_dir: str, symbol: str):
    logger = get_run_logger()
    logger.info(f"Saving data for {symbol} to JSON")
    os.makedirs(output_dir, exist_ok=True)
    try:
        async with aiofiles.open(os.path.join(output_dir, f"{symbol}.json"), "w") as f:
            await f.write(json.dumps(data))
    except Exception as e:
        logger.error(f"Error saving data for {symbol}: {e}")
        raise


# Задача для отправки уведомлений в Telegram
@task
async def notify_completion(message: str):
    await send_telegram_message(message)


# Основной поток обработки данных
@flow
async def data_processing_flow(file_path: str, output_dir: str):
    data = await load_data_from_csv(file_path)
    tasks = []
    for _, row in data.iterrows():
        symbol = extract_ticker(row)
        if symbol:
            task = asyncio.create_task(
                process_symbol_data(symbol, output_dir)
            )
            tasks.append(task)
        else:
            logger = get_run_logger()
            logger.warning(f"Ticker not found in row: {row}")


    await asyncio.gather(*tasks)

    await notify_completion("Data processing completed successfully.")


# Вспомогательная функция для обработки тикера
async def process_symbol_data(symbol: str, output_dir: str):
    api_data = await fetch_api_data(symbol)
    await save_to_json(api_data, output_dir, symbol)


if __name__ == "__main__":
    asyncio.run(data_processing_flow("data/input.csv", "data/output"))
