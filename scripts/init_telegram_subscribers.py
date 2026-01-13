#!/usr/bin/env python3
"""Initialize Telegram subscribers database with known users."""

import os
import sys
from pathlib import Path

# Set data directory for local development
os.environ["DATA_DIR"] = str(Path(__file__).parent.parent / "data")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.telegram_subscribers import TelegramSubscriberRepository
from src.database.connection import init_db


def main():
    """Initialize subscribers."""
    print("=" * 60)
    print("Initializing Telegram Subscribers")
    print("=" * 60)
    print()

    # Initialize database
    print("1. Initializing database...")
    init_db()
    print("   ✓ Database initialized")
    print()

    # Create repository
    repo = TelegramSubscriberRepository()

    # Add first subscriber
    print("2. Adding subscriber 1...")
    sub1 = repo.add_subscriber(
        chat_id="867719791",
        username="nblbn",
        first_name="K",
        last_name="C"
    )
    print(f"   ✓ Added: {sub1.first_name} {sub1.last_name} (@{sub1.username})")
    print(f"     Chat ID: {sub1.chat_id}")
    print()

    # Add second subscriber
    print("3. Adding subscriber 2...")
    sub2 = repo.add_subscriber(
        chat_id="8256764477",
        username=None,
        first_name="K",
        last_name="C"
    )
    print(f"   ✓ Added: {sub2.first_name} {sub2.last_name}")
    print(f"     Chat ID: {sub2.chat_id}")
    print()

    # Show all subscribers
    print("4. Verifying all subscribers...")
    subscribers = repo.get_all_active_subscribers()
    print(f"   Total subscribers: {len(subscribers)}")
    print()

    for i, sub in enumerate(subscribers, 1):
        print(f"   {i}. Chat ID: {sub.chat_id}")
        print(f"      Name: {sub.first_name} {sub.last_name}")
        if sub.username:
            print(f"      Username: @{sub.username}")
        print()

    print("=" * 60)
    print("✅ Telegram subscribers initialized successfully!")
    print("=" * 60)
    print()
    print("Next: Test broadcasting by calling /api/telegram/test")
    print()


if __name__ == "__main__":
    main()
