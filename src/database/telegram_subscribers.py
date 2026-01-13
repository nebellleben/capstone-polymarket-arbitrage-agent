"""Telegram subscribers repository."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.models.telegram_subscriber import TelegramSubscriber


class TelegramSubscriberRepository:
    """Repository for Telegram subscribers."""

    TABLE_NAME = "telegram_subscribers"

    def __init__(self):
        """Initialize repository and create table if needed."""
        self._create_table()

    def _create_table(self):
        """Create subscribers table if it doesn't exist."""
        db_manager = get_db()
        engine = db_manager.engine

        with engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                    chat_id TEXT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """))
            conn.commit()

    def add_subscriber(
        self,
        chat_id: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> TelegramSubscriber:
        """Add a new subscriber or reactivate existing one."""
        db_manager = get_db()
        engine = db_manager.engine

        with engine.connect() as conn:
            # Check if subscriber exists
            result = conn.execute(
                text(f"SELECT * FROM {self.TABLE_NAME} WHERE chat_id = :chat_id"),
                {"chat_id": chat_id}
            )
            existing = result.fetchone()

            if existing:
                # Reactivate if inactive
                if not existing[5]:  # is_active
                    conn.execute(text(f"""
                        UPDATE {self.TABLE_NAME}
                        SET is_active = 1,
                            username = :username,
                            first_name = :first_name,
                            last_name = :last_name
                        WHERE chat_id = :chat_id
                    """), {
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "chat_id": chat_id
                    })
                    conn.commit()
            else:
                # Insert new subscriber
                conn.execute(text(f"""
                    INSERT INTO {self.TABLE_NAME} (chat_id, username, first_name, last_name)
                    VALUES (:chat_id, :username, :first_name, :last_name)
                """), {
                    "chat_id": chat_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                })
                conn.commit()

        return self.get_subscriber(chat_id)

    def remove_subscriber(self, chat_id: str) -> bool:
        """Mark subscriber as inactive."""
        db_manager = get_db()
        engine = db_manager.engine

        with engine.connect() as conn:
            result = conn.execute(text(f"""
                UPDATE {self.TABLE_NAME}
                SET is_active = 0
                WHERE chat_id = :chat_id
            """), {"chat_id": chat_id})
            conn.commit()

            return result.rowcount > 0

    def get_subscriber(self, chat_id: str) -> Optional[TelegramSubscriber]:
        """Get subscriber by chat ID."""
        db_manager = get_db()
        engine = db_manager.engine

        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT chat_id, username, first_name, last_name, subscribed_at, is_active
                FROM {self.TABLE_NAME}
                WHERE chat_id = :chat_id
            """), {"chat_id": chat_id})

            row = result.fetchone()
            if not row:
                return None

            return TelegramSubscriber(
                chat_id=row[0],
                username=row[1],
                first_name=row[2],
                last_name=row[3],
                subscribed_at=datetime.fromisoformat(str(row[4])),
                is_active=bool(row[5])
            )

    def get_all_active_subscribers(self) -> List[TelegramSubscriber]:
        """Get all active subscribers."""
        db_manager = get_db()
        engine = db_manager.engine

        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT chat_id, username, first_name, last_name, subscribed_at, is_active
                FROM {self.TABLE_NAME}
                WHERE is_active = 1
                ORDER BY subscribed_at DESC
            """))

            return [
                TelegramSubscriber(
                    chat_id=row[0],
                    username=row[1],
                    first_name=row[2],
                    last_name=row[3],
                    subscribed_at=datetime.fromisoformat(str(row[4])),
                    is_active=bool(row[5])
                )
                for row in result.fetchall()
            ]

    def get_subscriber_count(self) -> int:
        """Get count of active subscribers."""
        db_manager = get_db()
        engine = db_manager.engine

        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(*)
                FROM {self.TABLE_NAME}
                WHERE is_active = 1
            """))

            return result.fetchone()[0]
