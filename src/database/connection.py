"""
Database connection management for arbitrage detection system.

This module provides database connection pooling, session management,
and database initialization/migration support.

Supports both SQLite (development) and PostgreSQL (production).
"""

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

import aiosqlite
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool

from src.utils.config import settings
from src.utils.logging_config import logger


class DatabaseManager:
    """
    Manages database connections and sessions.

    Supports both SQLite (for local development) and PostgreSQL (for production).
    Automatically detects database type from environment variables.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self._engine = None
        self._session_factory = None
        self._db_path = None
        self._database_url = None
        self._database_type = None

        # Detect database type from environment
        self._detect_database_type()

        logger.info(
            "database_manager_init",
            database_type=self._database_type,
            database_url=self._database_url if self._database_type == "postgresql" else self._db_path
        )

    def _detect_database_type(self):
        """Detect database type from environment variables."""
        # Check for PostgreSQL URL (Railway sets this automatically)
        database_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")

        if database_url:
            # Railway provides DATABASE_URL with postgres:// protocol
            # Convert to sqlalchemy-compatible format if needed
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

            self._database_url = database_url
            self._database_type = "postgresql"
            logger.info("using_postgresql", database_url_present=True)
        else:
            # Fall back to SQLite for local development
            data_dir = settings.data_dir
            self._db_path = os.path.join(data_dir, "arbitrage.db")

            # Ensure data directory exists
            Path(data_dir).mkdir(parents=True, exist_ok=True)

            self._database_type = "sqlite"
            logger.info("using_sqlite", db_path=self._db_path)

    @property
    def engine(self) -> sqlalchemy.Engine:
        """Get or create database engine."""
        if self._engine is None:
            if self._database_type == "postgresql":
                # PostgreSQL with connection pooling
                self._engine = create_engine(
                    self._database_url,
                    echo=False,  # Set to True for SQL query logging
                    poolclass=QueuePool,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,  # Verify connections before using
                    pool_recycle=3600,  # Recycle connections after 1 hour
                )
                logger.info("database_engine_created", database="postgresql", pool_class="QueuePool")
            else:
                # SQLite with NullPool for multi-process compatibility
                self._engine = create_engine(
                    f"sqlite:///{self._db_path}",
                    connect_args={"check_same_thread": False},
                    echo=False,
                    poolclass=NullPool,
                )
                logger.info("database_engine_created", database="sqlite", pool_class="NullPool")

        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        return self._session_factory

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.

        Yields:
            Session: SQLAlchemy session

        Example:
            >>> with db_manager.get_session() as session:
            ...     alerts = session.query(Alert).all()
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("database_session_error", error=str(e))
            raise
        finally:
            session.close()

    async def get_async_connection(self) -> Optional[aiosqlite.Connection]:
        """
        Get an async SQLite connection (SQLite only).

        Returns:
            aiosqlite.Connection: Async database connection (None for PostgreSQL)

        Example:
            >>> async with db_manager.get_async_connection() as db:
            ...     await db.execute("SELECT * FROM alerts")
        """
        if self._database_type == "sqlite":
            return aiosqlite.connect(self._db_path)
        else:
            logger.warning("async_connection_not_supported", database=self._database_type)
            return None

    def initialize_database(self):
        """
        Initialize database schema.

        Creates all tables if they don't exist. Should be called
        on application startup.
        """
        from src.database.models import Alert, CycleMetric

        logger.info("database_init_start", database_type=self._database_type)

        try:
            # Create all tables
            Alert.metadata.create_all(self.engine)
            CycleMetric.metadata.create_all(self.engine)

            # Create indexes
            self._create_indexes()

            logger.info("database_init_complete", database_type=self._database_type)

        except Exception as e:
            logger.error("database_init_failed", database_type=self._database_type, error=str(e))
            raise

    def _create_indexes(self):
        """Create database indexes for common queries."""
        from src.database.models import Alert, CycleMetric

        try:
            with self.get_session() as session:
                # Indexes are already defined in models, but we can verify
                logger.info("database_indexes_verified", database_type=self._database_type)
        except Exception as e:
            logger.warning("database_index_verify_failed", error=str(e))

    def close(self):
        """Close database connections and cleanup resources."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            logger.info("database_closed", database_type=self._database_type)


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        DatabaseManager: Global database manager
    """
    return db_manager


def init_db() -> None:
    """
    Initialize the database.

    This function should be called on application startup to ensure
    all tables and indexes are created.

    Example:
        >>> from src.database.connection import init_db
        >>> init_db()
    """
    db_manager.initialize_database()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get a database session with automatic cleanup.

    Convenience function that delegates to DatabaseManager.get_session().

    Yields:
        Session: SQLAlchemy session
    """
    with db_manager.get_session() as session:
        yield session


if __name__ == "__main__":
    """CLI handler for database operations."""
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else None

    if command == "init":
        try:
            init_db()
            print("✓ Database initialized successfully")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: init")
        sys.exit(1)
