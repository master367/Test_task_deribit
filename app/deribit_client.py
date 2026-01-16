import aiohttp
import logging

logger = logging.getLogger(__name__)

class DeribitClient:
    def __init__(self):
        self.base_url = "https://test.deribit.com/api/v2/public/get_index_price"
        # Добавляем заголовки, чтобы имитировать браузер
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def get_index_price(self, ticker: str):
        params = {"index_name": ticker}
        try:
            # Устанавливаем таймаут, чтобы запрос не висел вечно
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result", {}).get("index_price")
                    else:
                        error_text = await response.text()
                        logger.error(f"Error from Deribit: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Connection error to Deribit for {ticker}: {e}")
            return None