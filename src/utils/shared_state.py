"""
Thread-safe shared state for arbitrage detection system.

This module provides singleton classes for managing in-memory state
shared between the background worker and web server, with proper
locking for concurrent access.
"""

import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.alert import Alert
from src.utils.logging_config import logger


class ThreadSafeAlertStore:
    """
    Thread-safe store for alert history.

    Maintains a bounded list of recent alerts in memory with
    thread-safe access for concurrent reads and writes.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize alert store.

        Args:
            max_size: Maximum number of alerts to keep in memory
        """
        self._alerts: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self._max_size = max_size

    def add(self, alert: Alert) -> None:
        """
        Add alert to store.

        Args:
            alert: Alert object to add
        """
        with self._lock:
            alert_dict = {
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
                "timestamp": alert.timestamp.isoformat(),
            }

            self._alerts.append(alert_dict)

            # Maintain max size
            if len(self._alerts) > self._max_size:
                self._alerts = self._alerts[-self._max_size:]

            logger.debug("alert_added_to_store", alert_id=alert.id, total=len(self._alerts))

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent alerts.

        Args:
            limit: Maximum number of alerts to return

        Returns:
            List of alert dictionaries (most recent first)
        """
        with self._lock:
            return list(reversed(self._alerts[-limit:]))

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all alerts in store.

        Returns:
            List of all alert dictionaries
        """
        with self._lock:
            return list(self._alerts)

    def count(self) -> int:
        """Get total alert count."""
        with self._lock:
            return len(self._alerts)

    def clear(self) -> None:
        """Clear all alerts from store."""
        with self._lock:
            self._alerts.clear()
            logger.info("alert_store_cleared")


class ThreadSafeMetricsStore:
    """
    Thread-safe store for cycle metrics.

    Maintains a bounded list of recent cycle metrics in memory
    with thread-safe access for concurrent reads and writes.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize metrics store.

        Args:
            max_size: Maximum number of cycles to keep in memory
        """
        self._metrics: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self._max_size = max_size

    def add(self, metrics: "CycleMetrics") -> None:
        """
        Add cycle metrics to store.

        Args:
            metrics: CycleMetrics object to add
        """
        with self._lock:
            metrics_dict = {
                "cycle_id": metrics.cycle_id,
                "start_time": metrics.start_time.isoformat(),
                "end_time": metrics.end_time.isoformat(),
                "duration_seconds": metrics.duration_seconds,
                "news_articles_fetched": metrics.news_articles_fetched,
                "news_articles_new": metrics.news_articles_new,
                "markets_fetched": metrics.markets_fetched,
                "markets_with_prices": metrics.markets_with_prices,
                "impacts_analyzed": metrics.impacts_analyzed,
                "impacts_significant": metrics.impacts_significant,
                "reasoning_time_total": metrics.reasoning_time_total,
                "opportunities_detected": metrics.opportunities_detected,
                "opportunities_high_confidence": metrics.opportunities_high_confidence,
                "alerts_generated": metrics.alerts_generated,
                "api_calls": metrics.api_calls,
                "error_count": metrics.error_count,
                "news_to_alert_rate": metrics.news_to_alert_rate,
                "opportunity_detection_rate": metrics.opportunity_detection_rate,
            }

            self._metrics.append(metrics_dict)

            # Maintain max size
            if len(self._metrics) > self._max_size:
                self._metrics = self._metrics[-self._max_size:]

            logger.debug(
                "metrics_added_to_store",
                cycle_id=metrics.cycle_id,
                total=len(self._metrics)
            )

    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most recent cycle metrics.

        Args:
            limit: Maximum number of cycles to return

        Returns:
            List of cycle metric dictionaries (most recent first)
        """
        with self._lock:
            return list(reversed(self._metrics[-limit:]))

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all metrics in store.

        Returns:
            List of all cycle metric dictionaries
        """
        with self._lock:
            return list(self._metrics)

    def count(self) -> int:
        """Get total cycle count."""
        with self._lock:
            return len(self._metrics)

    def clear(self) -> None:
        """Clear all metrics from store."""
        with self._lock:
            self._metrics.clear()
            logger.info("metrics_store_cleared")


class ServiceState:
    """
    Tracks service state and status.

    Singleton class for maintaining service-wide state including
    worker status, uptime, and health metrics.
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
        self._start_time = datetime.utcnow()
        self._worker_running = False
        self._web_server_running = False
        self._current_cycle = 0
        self._last_cycle_time: Optional[datetime] = None
        self._lock = threading.RLock()

        logger.info("service_state_initialized")

    @property
    def uptime_seconds(self) -> float:
        """Get service uptime in seconds."""
        return (datetime.utcnow() - self._start_time).total_seconds()

    def set_worker_running(self, running: bool) -> None:
        """
        Set worker running status.

        Args:
            running: Whether worker is running
        """
        with self._lock:
            self._worker_running = running
            logger.info("worker_status_changed", running=running)

    def set_web_server_running(self, running: bool) -> None:
        """
        Set web server running status.

        Args:
            running: Whether web server is running
        """
        with self._lock:
            self._web_server_running = running
            logger.info("web_server_status_changed", running=running)

    def increment_cycle(self) -> int:
        """
        Increment cycle counter.

        Returns:
            New cycle number
        """
        with self._lock:
            self._current_cycle += 1
            self._last_cycle_time = datetime.utcnow()
            logger.debug("cycle_incremented", cycle=self._current_cycle)
            return self._current_cycle

    def get_status(self) -> Dict[str, Any]:
        """
        Get current service status.

        Returns:
            Dictionary with service status information
        """
        with self._lock:
            return {
                "uptime_seconds": round(self.uptime_seconds, 2),
                "worker_running": self._worker_running,
                "web_server_running": self._web_server_running,
                "current_cycle": self._current_cycle,
                "last_cycle_time": self._last_cycle_time.isoformat() if self._last_cycle_time else None,
                "start_time": self._start_time.isoformat(),
            }

    def is_healthy(self) -> bool:
        """
        Check if service is healthy.

        Returns:
            True if both worker and web server are running
        """
        with self._lock:
            return self._worker_running and self._web_server_running


# Global singleton instances
alert_store = ThreadSafeAlertStore()
metrics_store = ThreadSafeMetricsStore()
service_state = ServiceState()


def get_alert_store() -> ThreadSafeAlertStore:
    """Get the global alert store instance."""
    return alert_store


def get_metrics_store() -> ThreadSafeMetricsStore:
    """Get the global metrics store instance."""
    return metrics_store


def get_service_state() -> ServiceState:
    """Get the global service state instance."""
    return service_state
