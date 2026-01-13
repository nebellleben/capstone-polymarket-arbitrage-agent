"""Alert generation and formatting."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models.alert import Alert, AlertSeverity
from src.models.market import Market
from src.models.news import NewsArticle
from src.models.opportunity import Opportunity
from src.utils.config import settings
from src.utils.shared_state import get_alert_store
from src.database.repositories import AlertRepository
from src.notifications.telegram_notifier import create_telegram_notifier

from src.utils.logging_config import logger


class AlertGenerator:
    """
    Generate and manage alerts for arbitrage opportunities.

    This class:
    1. Creates alerts from opportunities
    2. Formats alerts for different output channels
    3. Manages alert history
    4. Exports alerts to JSON
    """

    def __init__(
        self,
        retention: int | None = None,
        export_path: Optional[Path] = None,
        enable_persistence: bool = True,
        enable_telegram: bool = True
    ):
        """
        Initialize the alert generator.

        Args:
            retention: Number of alerts to retain in memory
            export_path: Path to export alerts JSON file
            enable_persistence: Whether to persist alerts to database
            enable_telegram: Whether to enable Telegram notifications
        """
        self.retention = retention or settings.alert_retention
        self.export_path = export_path or Path("alerts.json")
        self.alert_history: list[Alert] = []
        self.alert_counts: dict[str, int] = {}
        self.enable_persistence = enable_persistence

        # Initialize database repository if persistence is enabled
        self.alert_repo = AlertRepository() if enable_persistence else None

        # Get shared state store
        self.alert_store = get_alert_store()

        # Initialize Telegram notifier
        self.enable_telegram = enable_telegram
        self.telegram_notifier = None
        if enable_telegram and settings.telegram_enabled:
            min_severity = AlertSeverity[settings.telegram_min_severity.upper()]
            self.telegram_notifier = create_telegram_notifier(
                bot_token=settings.telegram_bot_token,
                chat_id=settings.telegram_chat_id,
                enabled=settings.telegram_enabled,
                min_severity=min_severity
            )
            if self.telegram_notifier.is_enabled():
                logger.info("telegram_notifications_enabled")
            else:
                logger.info("telegram_notifications_disabled", reason="Configuration missing")
        else:
            logger.info("telegram_notifications_disabled", reason="Feature disabled")

    def create_alert(
        self,
        opportunity: Opportunity,
        news: NewsArticle,
        market: Market,
        reasoning: str
    ) -> Alert:
        """
        Create an alert from an opportunity.

        Args:
            opportunity: Detected opportunity
            news: Related news article
            market: Related market
            reasoning: AI reasoning explanation

        Returns:
            Alert object
        """
        alert = Alert.from_opportunity(
            opportunity=opportunity,
            news=news,
            market=market,
            reasoning=reasoning
        )

        # Add to history
        self._add_to_history(alert)

        # Persist to database if enabled
        if self.enable_persistence and self.alert_repo:
            try:
                alert_dict = self._alert_to_dict(alert)
                self.alert_repo.save(alert_dict)
                logger.debug("alert_persisted", alert_id=alert.id)
            except Exception as e:
                logger.error("alert_persistence_failed", alert_id=alert.id, error=str(e))

        # Update shared state
        try:
            self.alert_store.add(alert)
        except Exception as e:
            logger.error("alert_shared_state_failed", alert_id=alert.id, error=str(e))

        # Send Telegram notification
        if self.telegram_notifier and self.telegram_notifier.is_enabled():
            try:
                # Broadcast to all subscribers
                result = self.telegram_notifier.broadcast_alert(alert)
                if result.get("success"):
                    logger.info(
                        "telegram_broadcast_success",
                        alert_id=alert.id,
                        total=result.get("total_subscribers", 0),
                        success_count=result.get("success_count", 0)
                    )
            except Exception as e:
                logger.error("telegram_notification_failed", alert_id=alert.id, error=str(e))

        logger.info(
            "alert_created",
            alert_id=alert.id,
            severity=alert.severity,
            market_id=alert.market_id,
            confidence=alert.confidence
        )

        return alert

    def format_console(self, alert: Alert) -> str:
        """
        Format alert for console output.

        Args:
            alert: Alert to format

        Returns:
            Formatted string for console
        """
        severity_emoji = {
            AlertSeverity.CRITICAL: "🔴",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.INFO: "ℹ️"
        }

        emoji = severity_emoji.get(alert.severity, "•")

        return f"""
{emoji} {alert.title}
{'=' * 80}
Severity: {alert.severity}
Market: {alert.market_question}
News: {alert.news_title}
Current Price: {alert.current_price:.4f}
Expected Price: {alert.expected_price:.4f}
Discrepancy: {alert.discrepancy:.2%}
Confidence: {alert.confidence:.2%}
Recommended Action: {alert.recommended_action}

Reasoning:
{alert.reasoning}

News URL: {alert.news_url}
Alert ID: {alert.id}
{'=' * 80}
"""

    def format_json(self, alerts: list[Alert] | Alert) -> str:
        """
        Format alerts as JSON.

        Args:
            alerts: Alert or list of alerts

        Returns:
            JSON string
        """
        if isinstance(alerts, Alert):
            alerts = [alerts]

        data = [self._alert_to_dict(alert) for alert in alerts]
        return json.dumps(data, indent=2, default=str)

    def export_json(self, alerts: list[Alert] | None = None) -> Path:
        """
        Export alerts to JSON file.

        Args:
            alerts: Alerts to export (defaults to all alerts in history)

        Returns:
            Path to exported file
        """
        if alerts is None:
            alerts = self.alert_history

        data = [self._alert_to_dict(alert) for alert in alerts]

        with open(self.export_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(
            "alerts_exported",
            count=len(data),
            path=str(self.export_path)
        )

        return self.export_path

    def get_recent_alerts(
        self,
        limit: int = 10,
        severity: Optional[AlertSeverity] = None
    ) -> list[Alert]:
        """
        Get recent alerts from history.

        Args:
            limit: Maximum number of alerts to return
            severity: Filter by severity (optional)

        Returns:
            List of recent alerts
        """
        alerts = self.alert_history

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        # Sort by timestamp descending
        alerts = sorted(alerts, key=lambda a: a.timestamp, reverse=True)

        return alerts[:limit]

    def get_alert_stats(self) -> dict[str, any]:
        """
        Get statistics about alerts.

        Returns:
            Dictionary with alert statistics
        """
        if not self.alert_history:
            return {
                "total_alerts": 0,
                "by_severity": {},
                "avg_confidence": 0.0
            }

        by_severity = {}
        total_confidence = 0.0

        for alert in self.alert_history:
            severity = alert.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            total_confidence += alert.confidence

        return {
            "total_alerts": len(self.alert_history),
            "by_severity": by_severity,
            "avg_confidence": total_confidence / len(self.alert_history),
            "last_24h": sum(
                1 for a in self.alert_history
                if (datetime.utcnow() - a.timestamp).total_seconds() < 86400
            )
        }

    def _add_to_history(self, alert: Alert):
        """Add alert to history with retention management."""
        self.alert_history.append(alert)

        # Update counts
        severity = alert.severity.value
        self.alert_counts[severity] = self.alert_counts.get(severity, 0) + 1

        # Enforce retention limit
        if len(self.alert_history) > self.retention:
            # Remove oldest alert
            removed = self.alert_history.pop(0)
            logger.debug(
                "alert_evicted",
                alert_id=removed.id,
                history_size=len(self.alert_history)
            )

    def _alert_to_dict(self, alert: Alert) -> dict[str, any]:
        """Convert alert to dictionary for JSON serialization."""
        return {
            "id": alert.id,
            "opportunity_id": alert.opportunity_id,
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.message,
            "news_url": str(alert.news_url),
            "news_title": alert.news_title,
            "market_id": alert.market_id,
            "market_question": alert.market_question,
            "reasoning": alert.reasoning,
            "confidence": round(alert.confidence, 4),
            "current_price": round(alert.current_price, 4),
            "expected_price": round(alert.expected_price, 4),
            "discrepancy": round(alert.discrepancy, 4),
            "recommended_action": alert.recommended_action,
            "timestamp": alert.timestamp.isoformat()
        }

    def clear_history(self):
        """Clear alert history."""
        self.alert_history.clear()
        self.alert_counts.clear()
        logger.info("alert_history_cleared")
