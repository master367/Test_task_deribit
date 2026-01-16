from fastapi import FastAPI, Query, HTTPException
from datetime import datetime
from typing import List, Optional
from app.database import get_db, init_db
from app.models import PriceData, PriceResponse
from app.repository import PriceRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Price API",
    description="API for retrieving cryptocurrency prices from Deribit",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Crypto Price API is running"}


@app.get("/prices/all", response_model=List[PriceResponse], tags=["Prices"])
async def get_all_prices(ticker: str = Query(..., description="Currency ticker (e.g., btc_usd, eth_usd)")):
    """
    Get all saved prices for specified currency ticker

    - **ticker**: Currency ticker (required)
    """
    db = next(get_db())
    repository = PriceRepository(db)

    prices = repository.get_all_by_ticker(ticker.lower())

    if not prices:
        raise HTTPException(status_code=404, detail=f"No data found for ticker: {ticker}")

    return prices


@app.get("/prices/latest", response_model=PriceResponse, tags=["Prices"])
async def get_latest_price(ticker: str = Query(..., description="Currency ticker (e.g., btc_usd, eth_usd)")):
    """
    Get the latest price for specified currency ticker

    - **ticker**: Currency ticker (required)
    """
    db = next(get_db())
    repository = PriceRepository(db)

    price = repository.get_latest_by_ticker(ticker.lower())

    if not price:
        raise HTTPException(status_code=404, detail=f"No data found for ticker: {ticker}")

    return price


@app.get("/prices/filter", response_model=List[PriceResponse], tags=["Prices"])
async def get_prices_by_date(
        ticker: str = Query(..., description="Currency ticker (e.g., btc_usd, eth_usd)"),
        start_date: Optional[str] = Query(None, description="Start date in ISO format (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date in ISO format (YYYY-MM-DD)")
):
    """
    Get prices for specified currency ticker filtered by date range

    - **ticker**: Currency ticker (required)
    - **start_date**: Start date in ISO format (optional)
    - **end_date**: End date in ISO format (optional)
    """
    db = next(get_db())
    repository = PriceRepository(db)

    start_timestamp = None
    end_timestamp = None

    if start_date:
        try:
            start_timestamp = int(datetime.fromisoformat(start_date).timestamp())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

    if end_date:
        try:
            end_timestamp = int(datetime.fromisoformat(end_date).timestamp())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

    prices = repository.get_by_date_range(ticker.lower(), start_timestamp, end_timestamp)

    if not prices:
        raise HTTPException(status_code=404, detail=f"No data found for ticker: {ticker} in specified date range")

    return prices