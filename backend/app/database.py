"""
Database configuration and session management with security best practices
"""
from contextlib import contextmanager
from typing import Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.config import settings
from app.core.logger import logger

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
parsed_url = urlparse(SQLALCHEMY_DATABASE_URL)

# Common engine arguments for security
engine_args = {
    "pool_size": settings.DB_POOL_SIZE,  # Number of connections to maintain
    "max_overflow": settings.DB_MAX_OVERFLOW,  # Max number of connections to allow over pool_size
    "pool_timeout": settings.DB_POOL_TIMEOUT,  # Seconds to wait before timing out on getting a connection
    "pool_recycle": settings.DB_POOL_RECYCLE,  # Recycle connections after this many seconds
    "pool_pre_ping": True,  # Enable connection health checks
    "poolclass": QueuePool,  # Use QueuePool for connection pooling
}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": settings.DB_CONNECT_TIMEOUT
        },
        **engine_args
    )
else:
    # For PostgreSQL/MySQL, add SSL and other security settings
    connect_args = {
        "connect_timeout": settings.DB_CONNECT_TIMEOUT,
        "application_name": settings.PROJECT_NAME,  # Identify application in database logs
    }
    
    # Add SSL configuration for production
    if not settings.is_development():
        connect_args.update({
            "sslmode": "verify-full",
            "sslcert": settings.DB_SSL_CERT_PATH,
            "sslkey": settings.DB_SSL_KEY_PATH,
            "sslrootcert": settings.DB_SSL_ROOT_CERT_PATH,
        })
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args,
        **engine_args
    )

# Create session factory with security settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent expired object access issues
)

Base = declarative_base()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Database session context manager with enhanced error handling and logging
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise
    finally:
        db.close()

def validate_db_connection() -> bool:
    """
    Validate database connection on startup
    """
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection validation failed: {str(e)}")
        return False

# Add event listeners for connection pool monitoring
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    logger.debug("Database connection established")

@event.listens_for(Engine, "disconnect")
def receive_disconnect(dbapi_connection, connection_record):
    logger.debug("Database connection closed")

@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection retrieved from pool") 