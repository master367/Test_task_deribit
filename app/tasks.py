from celery import Celery
import asyncio
import time
import logging
from app.config import settings
from app.deribit_client import DeribitClient
from app.database import db_manager
from app.repository import PriceRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "crypto_prices",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'fetch-prices-every-minute': {
            'task': 'app.tasks.fetch_and_save_prices',
            'schedule': 60.0,  # Запуск каждую минуту
        },
    },
)


async def fetch_price_for_ticker(ticker: str) -> tuple[str, float, int]:
    """
    Получение цены для одного тикера
    """
    # Создаем объект клиента без использования 'async with'
    client = DeribitClient()
    # Вызываем метод напрямую
    price = await client.get_index_price(ticker)
    timestamp = int(time.time())
    return ticker, price, timestamp


@celery_app.task(name='app.tasks.fetch_and_save_prices')
def fetch_and_save_prices():
    """
    Задача Celery для сбора цен и сохранения в БД
    """
    logger.info("Starting price fetch task")

    session = db_manager.get_session()
    repository = PriceRepository(session)

    try:
        for ticker in settings.tickers:
            try:
                # Запуск асинхронной функции в синхронном контексте
                ticker_name, price, timestamp = asyncio.run(fetch_price_for_ticker(ticker))

                if price is not None:
                    repository.save_price(ticker_name, price, timestamp)
                    logger.info(f"Saved {ticker_name}: ${price} at timestamp {timestamp}")
                else:
                    logger.warning(f"Failed to fetch price for {ticker_name}")

            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")

        logger.info("Price fetch task completed successfully")

    except Exception as e:
        logger.error(f"Error in fetch_and_save_prices task: {str(e)}")
    finally:
        session.close()