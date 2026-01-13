#!/usr/bin/env python3
"""Test Telegram notification configuration."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.notifications.telegram_notifier import create_telegram_notifier
from src.models.alert import AlertSeverity
from src.utils.config import settings


def test_telegram_configuration():
    """Test Telegram notification setup."""
    print("=" * 60)
    print("Telegram Notification Test")
    print("=" * 60)
    print()

    # Check configuration
    print("Configuration Check:")
    print(f"  Bot Token: {'✓ Set' if settings.telegram_bot_token else '✗ Not set'}")
    print(f"  Chat ID: {'✓ Set' if settings.telegram_chat_id else '✗ Not set'}")
    print(f"  Enabled: {settings.telegram_enabled}")
    print(f"  Min Severity: {settings.telegram_min_severity}")
    print()

    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        print("❌ Telegram is not configured!")
        print()
        print("To enable Telegram notifications:")
        print("1. Create a bot via @BotFather on Telegram")
        print("2. Get your bot token and chat ID")
        print("3. Set environment variables:")
        print("   - TELEGRAM_BOT_TOKEN=your_token_here")
        print("   - TELEGRAM_CHAT_ID=your_chat_id_here")
        print("   - TELEGRAM_ENABLED=true")
        print()
        print("See: docs/notifications/telegram-setup-guide.md")
        return False

    # Create notifier
    print("Creating Telegram notifier...")
    min_severity = AlertSeverity[settings.telegram_min_severity.upper()]
    notifier = create_telegram_notifier(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
        enabled=settings.telegram_enabled,
        min_severity=min_severity
    )

    if not notifier.is_enabled():
        print("❌ Telegram notifier is not enabled!")
        return False

    print("✓ Notifier created successfully")
    print()

    # Send test message
    print("Sending test message to Telegram...")
    print(f"  Chat ID: {notifier.get_chat_id()}")
    print()

    success = notifier.send_test_message()

    if success:
        print("✅ Test message sent successfully!")
        print()
        print("Check your Telegram - you should have received a test message.")
        print()
        print("You'll now receive alerts when arbitrage opportunities are detected:")
        print("  🔴 CRITICAL - High confidence opportunities")
        print("  ⚠️  WARNING  - Medium confidence opportunities")
        print("  ℹ️  INFO     - Low confidence opportunities (if enabled)")
        print()
        print("To change which alerts you receive, modify TELEGRAM_MIN_SEVERITY:")
        print("  - INFO: Receive all alerts")
        print("  - WARNING: Receive WARNING and CRITICAL (default)")
        print("  - CRITICAL: Receive only CRITICAL alerts")
        return True
    else:
        print("❌ Failed to send test message!")
        print()
        print("Troubleshooting:")
        print("1. Verify bot token is correct:")
        print("   curl https://api.telegram.org/botYOUR_TOKEN/getMe")
        print()
        print("2. Verify chat ID is correct:")
        print("   - Send /start to your bot")
        print("   - Visit: https://api.telegram.org/botYOUR_TOKEN/getUpdates")
        print("   - Find your chat ID in the response")
        print()
        print("3. Check you've started a chat with your bot (send /start)")
        print()
        print("4. Check logs for detailed error messages:")
        print("   tail -f logs/arbitrage_agent.log | grep telegram")
        return False


if __name__ == "__main__":
    success = test_telegram_configuration()
    sys.exit(0 if success else 1)
