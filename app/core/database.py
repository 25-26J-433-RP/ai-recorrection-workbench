"""
Akura AI - Database Configuration

SQLAlchemy setup for Supabase PostgreSQL connection.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Create engine only if database URL is configured
if settings.database_url:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

Base = declarative_base()


def get_db():
    """Get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL in .env")
    try:
        db = SessionLocal()
        # Test connection
        db.execute("SELECT 1")
        yield db
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {str(e)}. Check DATABASE_URL and network connection.")
    finally:
        if 'db' in locals():
            db.close()


def init_db():
    """Initialize database tables."""
    if engine is not None:
        Base.metadata.create_all(bind=engine)
