"""
Thread-safe shared state for arbitrage detection system.

This module provides singleton classes for managing state
shared between the background worker and web server, with proper
locking for concurrent access and file-based cross-process state.
"""

import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models.alert import Alert
from src.utils.logging_config import logger

# File-based state directory for cross-process communication
STATE_DIR = Path(os.environ.get("STATE_DIR", "/tmp/state"))
STATE_DIR.mkdir(exist_ok=True)
WORKER_STATUS_FILE = STATE_DIR / "worker_status.json"


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
        from src.models.alert import AlertSeverity

        with self._lock:
            # Handle both Enum and string severity
            severity = alert.severity.value if isinstance(alert.severity, AlertSeverity) else alert.severity

            alert_dict = {
                "id": alert.id,
                "opportunity_id": alert.opportunity_id,
                "severity": severity,
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

    Uses file-based state for cross-process communication between
    the worker and web server.
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

    def _read_worker_status_file(self) -> Optional[Dict[str, Any]]:
        """Read worker status from file for cross-process communication."""
        try:
            if WORKER_STATUS_FILE.exists():
                import json
                with open(WORKER_STATUS_FILE, 'r') as f:
                    data = json.load(f)
                # Check if the worker is still alive (heartbeat within last 30 seconds)
                heartbeat = data.get("last_heartbeat")
                if heartbeat:
                    heartbeat_time = datetime.fromisoformat(heartbeat)
                    if (datetime.utcnow() - heartbeat_time).total_seconds() < 30:
                        return data
        except Exception as e:
            logger.debug("failed_to_read_worker_status", error=str(e))
        return None

    def _write_worker_status_file(self) -> None:
        """Write worker status to file for cross-process communication."""
        try:
            import json
            with open(WORKER_STATUS_FILE, 'w') as f:
                json.dump({
                    "worker_running": self._worker_running,
                    "current_cycle": self._current_cycle,
                    "last_heartbeat": datetime.utcnow().isoformat(),
                    "last_cycle_time": self._last_cycle_time.isoformat() if self._last_cycle_time else None,
                }, f)
        except Exception as e:
            logger.error("failed_to_write_worker_status", error=str(e))

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
            # Write to file for cross-process communication
            if running:
                self._write_worker_status_file()
            else:
                # Remove status file if worker stopped
                try:
                    WORKER_STATUS_FILE.unlink(missing_ok=True)
                except Exception:
                    pass
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
            # Update worker status file with new cycle info
            if self._worker_running:
                self._write_worker_status_file()
            logger.debug("cycle_incremented", cycle=self._current_cycle)
            return self._current_cycle

    def get_status(self) -> Dict[str, Any]:
        """
        Get current service status.

        Returns:
            Dictionary with service status information
        """
        with self._lock:
            # Check worker status file for cross-process state
            worker_status_from_file = self._read_worker_status_file()
            if worker_status_from_file:
                # Use the cross-process values
                worker_running = worker_status_from_file.get("worker_running", False)
                current_cycle = worker_status_from_file.get("current_cycle", 0)
                last_cycle_time = worker_status_from_file.get("last_cycle_time")
            else:
                # Fall back to in-process values
                worker_running = self._worker_running
                current_cycle = self._current_cycle
                last_cycle_time = self._last_cycle_time.isoformat() if self._last_cycle_time else None

            return {
                "uptime_seconds": round(self.uptime_seconds, 2),
                "worker_running": worker_running,
                "web_server_running": self._web_server_running,
                "current_cycle": current_cycle,
                "last_cycle_time": last_cycle_time,
                "start_time": self._start_time.isoformat(),
            }

    def is_healthy(self) -> bool:
        """
        Check if service is healthy.

        Returns:
            True if both worker and web server are running
        """
        with self._lock:
            # Check worker status file for cross-process state
            worker_status_from_file = self._read_worker_status_file()
            if worker_status_from_file:
                worker_running = worker_status_from_file.get("worker_running", False)
            else:
                worker_running = self._worker_running
            return worker_running and self._web_server_running


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
