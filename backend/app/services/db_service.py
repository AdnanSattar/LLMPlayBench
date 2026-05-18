"""
Database service.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import settings
from ..schemas.db_models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with Alembic migrations."""
    try:
        # First check if the DB exists by creating a connection
        connection = engine.connect()
        connection.close()
        logger.info("Database connection successful")

        # Run Alembic migrations
        run_migrations()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Fallback to creating tables directly if migrations fail
        logger.info("Falling back to direct table creation")
        Base.metadata.create_all(bind=engine)


def run_migrations():
    """Run Alembic migrations."""
    try:
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent.parent.absolute()

        # Change to the backend directory
        original_dir = os.getcwd()
        os.chdir(backend_dir)

        # Run Alembic migration command
        logger.info("Running database migrations with Alembic")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(f"Migration output: {result.stdout}")

        # Change back to the original directory
        os.chdir(original_dir)

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return False


def get_session() -> Session:
    """Create a new database session."""
    return SessionLocal()
