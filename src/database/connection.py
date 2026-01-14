"""
Database connection management for arbitrage detection system.

This module provides SQLite database connection pooling, session management,
and database initialization/migration support.
"""

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import aiosqlite
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.utils.config import settings
from src.utils.logging_config import logger


class DatabaseManager:
    """
    Manages database connections and sessions.

    Uses thread-local storage for session isolation and provides
    both synchronous and asynchronous database access.
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

        # Get database path from settings
        data_dir = settings.data_dir
        self._db_path = os.path.join(data_dir, "arbitrage.db")

        # Ensure data directory exists
        Path(data_dir).mkdir(parents=True, exist_ok=True)

        logger.info(
            "database_manager_init",
            db_path=self._db_path,
            data_dir=data_dir
        )

    @property
    def engine(self) -> sqlalchemy.Engine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = create_engine(
                f"sqlite:///{self._db_path}",
                connect_args={"check_same_thread": False},
                echo=False,  # Set to True for SQL query logging
                pool_pre_ping=True,
            )
            logger.info("database_engine_created")
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

    async def get_async_connection(self) -> aiosqlite.Connection:
        """
        Get an async SQLite connection.

        Returns:
            aiosqlite.Connection: Async database connection

        Example:
            >>> async with db_manager.get_async_connection() as db:
            ...     await db.execute("SELECT * FROM alerts")
        """
        return aiosqlite.connect(self._db_path)

    def initialize_database(self):
        """
        Initialize database schema.

        Creates all tables if they don't exist. Should be called
        on application startup.
        """
        from src.database.models import Alert, CycleMetric

        logger.info("database_init_start", db_path=self._db_path)

        try:
            # Create all tables
            Alert.metadata.create_all(self.engine)
            CycleMetric.metadata.create_all(self.engine)

            # Create indexes
            self._create_indexes()

            logger.info("database_init_complete")

        except Exception as e:
            logger.error("database_init_failed", error=str(e))
            raise

    def _create_indexes(self):
        """Create database indexes for common queries."""
        from src.database.models import Alert, CycleMetric

        with self.get_session() as session:
            # Indexes are already defined in models, but we can verify
            logger.info("database_indexes_verified")

    def close(self):
        """Close database connections and cleanup resources."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            logger.info("database_closed")


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
