import aiohttp
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class DeribitClient:
    """Client for interacting with Deribit API"""

    def __init__(self, api_url: str = settings.deribit_api_url):
        self.api_url = api_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Context manager entry - create session"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        if self.session:
            await self.session.close()

    async def get_index_price(self, ticker: str) -> Optional[float]:
        """
        Get current index price for a ticker from Deribit

        Args:
            ticker: Currency ticker (e.g., 'btc_usd', 'eth_usd')

        Returns:
            Current index price or None if request fails
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use 'async with' context manager.")

        # Convert ticker format: btc_usd -> BTC
        currency = ticker.split('_')[0].upper()

        endpoint = f"{self.api_url}/public/get_index_price"
        params = {"index_name": f"{currency.lower()}_usd"}

        try:
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("result"):
                        price = data["result"].get("index_price")
                        logger.info(f"Retrieved {ticker} price: {price}")
                        return price
                    else:
                        logger.error(f"No result in response for {ticker}")
                else:
                    logger.error(f"Failed to get price for {ticker}: status {response.status}")

        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {str(e)}")

        return None