"""
Data access layer for arbitrage detection system.

This module provides repository classes for database operations
with batch support and query optimization.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import Alert, CycleMetric
from src.utils.logging_config import logger


class AlertRepository:
    """
    Repository for Alert database operations.

    Provides CRUD operations and query methods with support for
    filtering, pagination, and batch operations.
    """

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize repository.

        Args:
            db: Optional database session. If None, uses context manager.
        """
        self.db = db

    def save(self, alert_dict: Dict[str, Any]) -> Alert:
        """
        Save an alert to the database.

        Args:
            alert_dict: Alert data as dictionary

        Returns:
            Alert: Created Alert ORM object
        """
        db = self.db or get_db().get_session().__enter__()

        try:
            alert = Alert(**alert_dict)
            db.add(alert)
            db.commit()
            db.refresh(alert)

            logger.debug("alert_saved", alert_id=alert.id)
            return alert

        except Exception as e:
            db.rollback()
            logger.error("alert_save_failed", error=str(e))
            raise

    def save_batch(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Save multiple alerts in a single transaction.

        Args:
            alerts: List of alert dictionaries

        Returns:
            int: Number of alerts saved
        """
        if not alerts:
            return 0

        db = self.db or get_db().get_session().__enter__()

        try:
            alert_objects = [Alert(**alert_data) for alert_data in alerts]
            db.add_all(alert_objects)
            db.commit()

            logger.info("alerts_saved_batch", count=len(alerts))
            return len(alerts)

        except Exception as e:
            db.rollback()
            logger.error("alerts_batch_save_failed", error=str(e))
            raise

    def get_by_id(self, alert_id: str) -> Optional[Alert]:
        """
        Get alert by ID.

        Args:
            alert_id: Alert identifier

        Returns:
            Alert object or None
        """
        db = self.db or get_db().get_session().__enter__()
        return db.query(Alert).filter(Alert.id == alert_id).first()

    def get_recent(
        self,
        limit: int = 10,
        severity: Optional[str] = None,
        min_confidence: Optional[float] = None
    ) -> List[Alert]:
        """
        Get recent alerts with optional filtering.

        Args:
            limit: Maximum number of alerts to return
            severity: Filter by severity (INFO, WARNING, CRITICAL)
            min_confidence: Minimum confidence level

        Returns:
            List of Alert objects
        """
        db = self.db or get_db().get_session().__enter__()

        query = db.query(Alert).order_by(Alert.timestamp.desc())

        if severity:
            query = query.filter(Alert.severity == severity)

        if min_confidence is not None:
            query = query.filter(Alert.confidence >= min_confidence)

        return query.limit(limit).all()

    def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
        severity: Optional[str] = None,
        min_confidence: Optional[float] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Alert]:
        """
        Get alerts with pagination and filtering.

        Args:
            limit: Maximum number of alerts (default: 50, max: 100)
            offset: Pagination offset
            severity: Filter by severity
            min_confidence: Minimum confidence level
            start_time: Filter alerts after this time
            end_time: Filter alerts before this time

        Returns:
            List of Alert objects
        """
        db = self.db or get_db().get_session().__enter__()

        query = db.query(Alert).order_by(Alert.timestamp.desc())

        if severity:
            query = query.filter(Alert.severity == severity)

        if min_confidence is not None:
            query = query.filter(Alert.confidence >= min_confidence)

        if start_time:
            query = query.filter(Alert.timestamp >= start_time)

        if end_time:
            query = query.filter(Alert.timestamp <= end_time)

        return query.limit(min(limit, 100)).offset(offset).all()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get alert statistics.

        Returns:
            Dictionary with alert counts by severity and other stats
        """
        db = self.db or get_db().get_session().__enter__()

        total = db.query(func.count(Alert.id)).scalar()

        by_severity = {}
        for severity in ["INFO", "WARNING", "CRITICAL"]:
            count = db.query(func.count(Alert.id)).filter(
                Alert.severity == severity
            ).scalar()
            by_severity[severity] = count

        avg_confidence = db.query(func.avg(Alert.confidence)).scalar() or 0.0

        last_alert = db.query(Alert).order_by(
            Alert.timestamp.desc()
        ).first()

        last_24h = db.query(func.count(Alert.id)).filter(
            Alert.timestamp >= datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        ).scalar()

        return {
            "total_alerts": total,
            "by_severity": by_severity,
            "avg_confidence": round(avg_confidence, 4),
            "last_alert_timestamp": last_alert.timestamp if last_alert else None,
            "last_24h": last_24h,
        }

    def count(self) -> int:
        """Get total alert count."""
        db = self.db or get_db().get_session().__enter__()
        return db.query(func.count(Alert.id)).scalar()


class MetricsRepository:
    """
    Repository for CycleMetric database operations.

    Provides CRUD operations and aggregation methods for
    detection cycle performance metrics.
    """

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize repository.

        Args:
            db: Optional database session. If None, uses context manager.
        """
        self.db = db

    def save(self, metric_dict: Dict[str, Any]) -> CycleMetric:
        """
        Save cycle metrics to database.

        Args:
            metric_dict: Metric data as dictionary

        Returns:
            CycleMetric: Created CycleMetric ORM object
        """
        db = self.db or get_db().get_session().__enter__()

        try:
            metric = CycleMetric(**metric_dict)
            db.add(metric)
            db.commit()
            db.refresh(metric)

            logger.debug("metric_saved", cycle_id=metric.cycle_id)
            return metric

        except Exception as e:
            db.rollback()
            logger.error("metric_save_failed", error=str(e))
            raise

    def get_by_id(self, cycle_id: str) -> Optional[CycleMetric]:
        """
        Get cycle metrics by ID.

        Args:
            cycle_id: Cycle identifier

        Returns:
            CycleMetric object or None
        """
        db = self.db or get_db().get_session().__enter__()
        return db.query(CycleMetric).filter(
            CycleMetric.cycle_id == cycle_id
        ).first()

    def get_recent(self, limit: int = 20) -> List[CycleMetric]:
        """
        Get recent cycle metrics.

        Args:
            limit: Maximum number of cycles to return

        Returns:
            List of CycleMetric objects
        """
        db = self.db or get_db().get_session().__enter__()
        return db.query(CycleMetric).order_by(
            CycleMetric.start_time.desc()
        ).limit(limit).all()

    def get_aggregated(self, cycles: int = 10) -> Dict[str, Any]:
        """
        Get aggregated metrics for recent cycles.

        Args:
            cycles: Number of recent cycles to aggregate

        Returns:
            Dictionary with aggregated statistics
        """
        db = self.db or get_db().get_session().__enter__()

        recent_cycles = db.query(CycleMetric).order_by(
            CycleMetric.start_time.desc()
        ).limit(cycles).all()

        if not recent_cycles:
            return {
                "period": {"cycles_analyzed": 0, "duration_hours": 0},
                "performance": {},
                "api_usage": {},
                "opportunities": {},
                "alerts": {},
            }

        total_duration = sum(c.duration_seconds for c in recent_cycles)
        avg_duration = total_duration / len(recent_cycles)

        total_opportunities = sum(c.opportunities_detected for c in recent_cycles)
        total_alerts = sum(c.alerts_generated for c in recent_cycles)
        total_errors = sum(c.error_count for c in recent_cycles)

        # Aggregate API calls from JSON
        api_calls = {}
        for cycle in recent_cycles:
            try:
                calls = json.loads(c.api_calls_json)
                for key, value in calls.items():
                    api_calls[key] = api_calls.get(key, 0) + value
            except (json.JSONDecodeError, TypeError):
                pass

        # Alerts by severity (need to join with alerts table)
        alerts_by_cycle = [c.alerts_generated for c in recent_cycles]

        return {
            "period": {
                "cycles_analyzed": len(recent_cycles),
                "duration_hours": round(total_duration / 3600, 2),
            },
            "performance": {
                "avg_cycle_duration_seconds": round(avg_duration, 2),
                "avg_opportunities_per_cycle": round(
                    total_opportunities / len(recent_cycles), 2
                ),
                "avg_alerts_per_cycle": round(
                    total_alerts / len(recent_cycles), 2
                ),
                "total_errors": total_errors,
                "error_rate": round(total_errors / len(recent_cycles), 2),
            },
            "api_usage": api_calls,
            "opportunities": {
                "total_detected": total_opportunities,
                "by_cycle": [c.opportunities_detected for c in recent_cycles],
            },
            "alerts": {
                "total_generated": total_alerts,
                "by_cycle": alerts_by_cycle,
            },
        }

    def count(self) -> int:
        """Get total cycle count."""
        db = self.db or get_db().get_session().__enter__()
        return db.query(func.count(CycleMetric.cycle_id)).scalar()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for all cycles.

        Returns:
            Dictionary with performance statistics
        """
        db = self.db or get_db().get_session().__enter__()

        total_cycles = db.query(func.count(CycleMetric.cycle_id)).scalar()

        if total_cycles == 0:
            return {
                "total_cycles": 0,
                "avg_duration_seconds": 0,
                "min_duration_seconds": 0,
                "max_duration_seconds": 0,
                "total_opportunities": 0,
                "total_alerts": 0,
            }

        avg_duration = db.query(func.avg(CycleMetric.duration_seconds)).scalar() or 0
        min_duration = db.query(func.min(CycleMetric.duration_seconds)).scalar() or 0
        max_duration = db.query(func.max(CycleMetric.duration_seconds)).scalar() or 0

        total_opportunities = db.query(
            func.sum(CycleMetric.opportunities_detected)
        ).scalar() or 0

        total_alerts = db.query(func.sum(CycleMetric.alerts_generated)).scalar() or 0

        return {
            "total_cycles": total_cycles,
            "avg_duration_seconds": round(avg_duration, 2),
            "min_duration_seconds": round(min_duration, 2),
            "max_duration_seconds": round(max_duration, 2),
            "total_opportunities": total_opportunities,
            "total_alerts": total_alerts,
        }
