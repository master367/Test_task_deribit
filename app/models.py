from sqlalchemy import Column, Integer, String, Float, BigInteger, Index
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import Optional

Base = declarative_base()


class PriceData(Base):
    """SQLAlchemy model for storing cryptocurrency prices"""
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False, index=True)

    __table_args__ = (
        Index('ix_ticker_timestamp', 'ticker', 'timestamp'),
    )


class PriceResponse(BaseModel):
    """Pydantic model for API responses"""
    id: int
    ticker: str
    price: float
    timestamp: int

    class Config:
        from_attributes = True