from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models import Base
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connection and session lifecycle"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()


# Global database manager instance
db_manager = DatabaseManager(settings.database_url)


def get_db():
    """Dependency for getting database session"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    db_manager.create_tables()