from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import PriceData


class PriceRepository:
    """Repository pattern for database operations with price data"""

    def __init__(self, session: Session):
        self.session = session

    def save_price(self, ticker: str, price: float, timestamp: int) -> PriceData:
        """
        Save a new price record to database

        Args:
            ticker: Currency ticker symbol
            price: Current price
            timestamp: Unix timestamp

        Returns:
            Created PriceData object
        """
        price_data = PriceData(ticker=ticker, price=price, timestamp=timestamp)
        self.session.add(price_data)
        self.session.commit()
        self.session.refresh(price_data)
        return price_data

    def get_all_by_ticker(self, ticker: str) -> List[PriceData]:
        """
        Get all price records for a specific ticker

        Args:
            ticker: Currency ticker symbol

        Returns:
            List of PriceData objects
        """
        return self.session.query(PriceData).filter(
            PriceData.ticker == ticker
        ).order_by(PriceData.timestamp.desc()).all()

    def get_latest_by_ticker(self, ticker: str) -> Optional[PriceData]:
        """
        Get the most recent price for a specific ticker

        Args:
            ticker: Currency ticker symbol

        Returns:
            Latest PriceData object or None
        """
        return self.session.query(PriceData).filter(
            PriceData.ticker == ticker
        ).order_by(PriceData.timestamp.desc()).first()

    def get_by_date_range(
            self,
            ticker: str,
            start_timestamp: Optional[int] = None,
            end_timestamp: Optional[int] = None
    ) -> List[PriceData]:
        """
        Get price records filtered by date range

        Args:
            ticker: Currency ticker symbol
            start_timestamp: Start of date range (Unix timestamp)
            end_timestamp: End of date range (Unix timestamp)

        Returns:
            List of PriceData objects within date range
        """
        query = self.session.query(PriceData).filter(PriceData.ticker == ticker)

        if start_timestamp is not None:
            query = query.filter(PriceData.timestamp >= start_timestamp)

        if end_timestamp is not None:
            query = query.filter(PriceData.timestamp <= end_timestamp)

        return query.order_by(PriceData.timestamp.desc()).all()