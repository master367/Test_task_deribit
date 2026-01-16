import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base, PriceData
import time

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
def sample_data(test_db):
    """Insert sample data for testing"""
    db = TestingSessionLocal()
    timestamp = int(time.time())

    prices = [
        PriceData(ticker="btc_usd", price=45000.50, timestamp=timestamp - 3600),
        PriceData(ticker="btc_usd", price=45100.75, timestamp=timestamp - 1800),
        PriceData(ticker="btc_usd", price=45200.25, timestamp=timestamp),
        PriceData(ticker="eth_usd", price=2500.30, timestamp=timestamp),
    ]

    db.add_all(prices)
    db.commit()
    db.close()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_all_prices_success(client, sample_data):
    """Test getting all prices for a ticker"""
    response = client.get("/prices/all?ticker=btc_usd")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(item["ticker"] == "btc_usd" for item in data)


def test_get_all_prices_not_found(client, sample_data):
    """Test getting prices for non-existent ticker"""
    response = client.get("/prices/all?ticker=doge_usd")
    assert response.status_code == 404


def test_get_all_prices_missing_ticker(client, sample_data):
    """Test getting prices without ticker parameter"""
    response = client.get("/prices/all")
    assert response.status_code == 422


def test_get_latest_price_success(client, sample_data):
    """Test getting latest price for a ticker"""
    response = client.get("/prices/latest?ticker=btc_usd")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "btc_usd"
    assert data["price"] == 45200.25


def test_get_latest_price_not_found(client, sample_data):
    """Test getting latest price for non-existent ticker"""
    response = client.get("/prices/latest?ticker=doge_usd")
    assert response.status_code == 404


def test_get_prices_by_date_success(client, sample_data):
    """Test filtering prices by date"""
    from datetime import datetime, timedelta

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    response = client.get(f"/prices/filter?ticker=btc_usd&start_date={yesterday}&end_date={today}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_prices_invalid_date_format(client, sample_data):
    """Test invalid date format"""
    response = client.get("/prices/filter?ticker=btc_usd&start_date=invalid-date")
    assert response.status_code == 400


def test_case_insensitive_ticker(client, sample_data):
    """Test that ticker is case-insensitive"""
    response1 = client.get("/prices/latest?ticker=btc_usd")
    response2 = client.get("/prices/latest?ticker=BTC_USD")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["price"] == response2.json()["price"]