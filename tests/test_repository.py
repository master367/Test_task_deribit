import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.repository import PriceRepository
import time

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_repo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def repository(db_session):
    """Create repository instance"""
    return PriceRepository(db_session)


def test_save_price(repository):
    """Test saving a price record"""
    ticker = "btc_usd"
    price = 45000.50
    timestamp = int(time.time())

    result = repository.save_price(ticker, price, timestamp)

    assert result.id is not None
    assert result.ticker == ticker
    assert result.price == price
    assert result.timestamp == timestamp


def test_get_all_by_ticker(repository):
    """Test retrieving all prices for a ticker"""
    ticker = "btc_usd"
    timestamp = int(time.time())

    # Save multiple prices
    repository.save_price(ticker, 45000.0, timestamp - 3600)
    repository.save_price(ticker, 45500.0, timestamp - 1800)
    repository.save_price(ticker, 46000.0, timestamp)

    results = repository.get_all_by_ticker(ticker)

    assert len(results) == 3
    assert all(r.ticker == ticker for r in results)
    # Should be ordered by timestamp descending
    assert results[0].timestamp >= results[1].timestamp >= results[2].timestamp


def test_get_latest_by_ticker(repository):
    """Test retrieving the latest price for a ticker"""
    ticker = "eth_usd"
    timestamp = int(time.time())

    repository.save_price(ticker, 2500.0, timestamp - 3600)
    repository.save_price(ticker, 2600.0, timestamp - 1800)
    latest = repository.save_price(ticker, 2700.0, timestamp)

    result = repository.get_latest_by_ticker(ticker)

    assert result is not None
    assert result.price == latest.price
    assert result.timestamp == latest.timestamp


def test_get_latest_by_ticker_not_found(repository):
    """Test retrieving latest price for non-existent ticker"""
    result = repository.get_latest_by_ticker("nonexistent_ticker")
    assert result is None


def test_get_by_date_range(repository):
    """Test filtering prices by date range"""
    ticker = "btc_usd"
    base_time = int(time.time())

    # Create prices at different times
    repository.save_price(ticker, 45000.0, base_time - 7200)  # 2 hours ago
    repository.save_price(ticker, 45500.0, base_time - 3600)  # 1 hour ago
    repository.save_price(ticker, 46000.0, base_time - 1800)  # 30 min ago
    repository.save_price(ticker, 46500.0, base_time)  # now

    # Query for prices from 1.5 hours ago to 30 min ago
    results = repository.get_by_date_range(
        ticker,
        start_timestamp=base_time - 5400,
        end_timestamp=base_time - 1800
    )

    assert len(results) == 2
    assert all(r.ticker == ticker for r in results)


def test_get_by_date_range_start_only(repository):
    """Test filtering with only start date"""
    ticker = "btc_usd"
    base_time = int(time.time())

    repository.save_price(ticker, 45000.0, base_time - 7200)
    repository.save_price(ticker, 45500.0, base_time - 3600)
    repository.save_price(ticker, 46000.0, base_time)

    results = repository.get_by_date_range(ticker, start_timestamp=base_time - 4000)

    assert len(results) == 2


def test_get_by_date_range_end_only(repository):
    """Test filtering with only end date"""
    ticker = "btc_usd"
    base_time = int(time.time())

    repository.save_price(ticker, 45000.0, base_time - 7200)
    repository.save_price(ticker, 45500.0, base_time - 3600)
    repository.save_price(ticker, 46000.0, base_time)

    results = repository.get_by_date_range(ticker, end_timestamp=base_time - 4000)

    assert len(results) == 1