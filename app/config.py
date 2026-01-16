from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration settings"""

    # Database
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "db"
    postgres_port: str = "5432"
    postgres_db: str = "crypto_prices"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # Deribit API
    deribit_api_url: str = "https://www.deribit.com/api/v2"

    # Tickers to track
    tickers: List[str] = ["btc_usd", "eth_usd"]

    @property
    def database_url(self) -> str:
        """Construct database URL from components"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()