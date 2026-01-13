"""Telegram notification module for arbitrage alerts."""

import os
import urllib.parse
from typing import Optional

import requests

from src.models.alert import Alert, AlertSeverity
from src.utils.logging_config import logger


class TelegramNotifier:
    """
    Send arbitrage alerts to Telegram.

    Uses the Telegram Bot API to send formatted alerts to a configured chat.
    """

    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: bool = True,
        min_severity: AlertSeverity = AlertSeverity.WARNING
    ):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token (from @BotFather)
            chat_id: Chat ID to send alerts to
            enabled: Whether notifications are enabled
            min_severity: Minimum severity level to send
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = enabled and bool(self.bot_token and self.chat_id)
        self.min_severity = min_severity

        if not self.enabled:
            logger.info(
                "telegram_notifier_disabled",
                reason="Configuration missing" if not (self.bot_token and self.chat_id) else "Explicitly disabled"
            )
        else:
            logger.info(
                "telegram_notifier_initialized",
                chat_id=self.chat_id,
                min_severity=min_severity.value
            )

    def is_enabled(self) -> bool:
        """Check if Telegram notifications are enabled."""
        return self.enabled

    def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert to Telegram.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("telegram_notification_skipped", alert_id=alert.id, reason="Not enabled")
            return False

        # Check severity threshold
        if self._severity_below_threshold(alert.severity):
            logger.debug(
                "telegram_notification_skipped",
                alert_id=alert.id,
                reason=f"Severity {alert.severity.value} below {self.min_severity.value}"
            )
            return False

        try:
            message = self._format_alert(alert)
            success = self._send_message(message)

            if success:
                logger.info(
                    "telegram_alert_sent",
                    alert_id=alert.id,
                    severity=alert.severity.value
                )
            else:
                logger.error(
                    "telegram_alert_failed",
                    alert_id=alert.id,
                    reason="API request failed"
                )

            return success

        except Exception as e:
            logger.error(
                "telegram_alert_error",
                alert_id=alert.id,
                error=str(e)
            )
            return False

    def send_test_message(self) -> bool:
        """
        Send a test message to verify Telegram configuration.

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.warning("telegram_test_failed", reason="Not enabled")
            return False

        message = "🔔 *Polymarket Arbitrage Agent*\n\n✅ Telegram notifications are working!\n\nYou'll receive alerts here when arbitrage opportunities are detected."

        try:
            success = self._send_message(message)

            if success:
                logger.info("telegram_test_sent", chat_id=self.chat_id)
            else:
                logger.error("telegram_test_failed", reason="API request failed")

            return success

        except Exception as e:
            logger.error("telegram_test_error", error=str(e))
            return False

    def _send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message via Telegram Bot API.

        Args:
            message: Message text to send
            parse_mode: Parse mode (Markdown or HTML)

        Returns:
            True if successful
        """
        url = self.TELEGRAM_API_URL.format(token=self.bot_token, method="sendMessage")

        params = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get("ok", False)

        except requests.RequestException as e:
            logger.error(
                "telegram_api_error",
                error=str(e),
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            )
            return False

    def _format_alert(self, alert: Alert) -> str:
        """
        Format alert for Telegram message.

        Args:
            alert: Alert to format

        Returns:
            Formatted message string
        """
        # Severity emojis
        severity_emoji = {
            AlertSeverity.CRITICAL: "🔴",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.INFO: "ℹ️"
        }

        emoji = severity_emoji.get(alert.severity, "•")

        # Build message with Markdown formatting
        message = f"""{emoji} *{alert.title}*

*Severity:* {alert.severity.value}
*Confidence:* {alert.confidence:.1%}

💼 *Market:*
{alert.market_question}

*Current Price:* {alert.current_price:.4f}
*Expected Price:* {alert.expected_price:.4f}
*Discrepancy:* {alert.discrepancy:.2%}

📰 *News:*
[{alert.news_title}]({alert.news_url})

🧠 *Reasoning:*
{alert.reasoning[:300]}{'...' if len(alert.reasoning) > 300 else ''}

🎯 *Recommended Action:* {alert.recommended_action}

_Alert ID: {alert.id}_"""

        return message

    def _severity_below_threshold(self, severity: AlertSeverity) -> bool:
        """Check if severity is below the minimum threshold."""
        severity_order = {
            AlertSeverity.INFO: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.CRITICAL: 2
        }

        return severity_order.get(severity, 0) < severity_order.get(self.min_severity, 1)

    def get_chat_id(self) -> Optional[str]:
        """
        Get the configured chat ID.

        Returns:
            Chat ID or None if not configured
        """
        return self.chat_id


def create_telegram_notifier(
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
    enabled: bool = True,
    min_severity: AlertSeverity = AlertSeverity.WARNING
) -> TelegramNotifier:
    """
    Factory function to create a Telegram notifier.

    Args:
        bot_token: Telegram bot token (from @BotFather)
        chat_id: Chat ID to send alerts to
        enabled: Whether notifications are enabled
        min_severity: Minimum severity level to send

    Returns:
        Configured TelegramNotifier instance
    """
    return TelegramNotifier(
        bot_token=bot_token,
        chat_id=chat_id,
        enabled=enabled,
        min_severity=min_severity
    )
