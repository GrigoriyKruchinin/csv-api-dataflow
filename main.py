import os
import json
import asyncio
from datetime import timedelta

import aiofiles
from aiohttp import ClientSession, ClientTimeout

from concurrent.futures import ThreadPoolExecutor
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
import pandas as pd
from prefect.deployments.runner import DockerImage

from config import INPUT_FILE_PATH, OUTPUT_DIR
from utils import extract_ticker, fetch_data_from_api, send_telegram_message


semaphore = asyncio.Semaphore(5)
api_queue = asyncio.Queue(maxsize=5)


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


@task(
    retries=3,
    retry_delay_seconds=10,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
async def fetch_api_data(symbol: str) -> dict:
    logger = get_run_logger()
    logger.info(f"Fetching data for {symbol}")
    await api_queue.put(symbol)
    async with semaphore:
        async with ClientSession(timeout=ClientTimeout(total=30)) as session:
            api_data = await fetch_data_from_api(symbol, session)
    await api_queue.get()
    return api_data


@task()
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


@task
async def notify_completion(message: str):
    await send_telegram_message(message)


async def fetch_and_save(symbol: str, output_dir: str):
    api_data = await fetch_api_data(symbol)
    await save_to_json(api_data, output_dir, symbol)


@flow
async def data_processing_flow():
    data = await load_data_from_csv(INPUT_FILE_PATH)
    symbols = [extract_ticker(row) for _, row in data.iterrows() if extract_ticker(row)]

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            loop.run_in_executor(
                executor, lambda s=symbol: asyncio.run(fetch_and_save(s, OUTPUT_DIR))
            )
            for symbol in symbols
        ]

        await asyncio.gather(*futures)

    await notify_completion("Data processing completed successfully.")


if __name__ == "__main__":
    data_processing_flow.deploy(
        name="my-custom-dockerfile-deployment",
        work_pool_name="my-docker-pool",
        image=DockerImage(
            name="prefecthq/prefect", tag="latest", dockerfile="Dockerfile"
        ),
        push=False,
    )
