import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from .models import Base

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/candidate_screening")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_database() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseConnection:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    async def connect(self):
        """Initialize database connection"""
        create_tables()
        return True
    
    async def disconnect(self):
        """Close database connection"""
        self.engine.dispose()
    
    def get_session(self) -> Session:
        """Get database session"""
        return SessionLocal()

# Global database instance
db_connection = DatabaseConnection()
