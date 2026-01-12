"""Performance tracker for monitoring system performance."""

import time
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional

import structlog

from src.utils.metrics import CycleMetrics

logger = structlog.get_logger()


class PerformanceTracker:
    """Track performance metrics for the arbitrage detection system."""

    def __init__(self):
        """Initialize performance tracker."""
        self.cycle_timings: Dict[str, List[float]] = {}
        self.api_latencies: Dict[str, List[float]] = {}
        self.component_timings: Dict[str, List[float]] = {}

    def record_cycle_timing(self, cycle_id: str, duration: float):
        """Record total cycle duration."""
        if cycle_id not in self.cycle_timings:
            self.cycle_timings[cycle_id] = []
        self.cycle_timings[cycle_id].append(duration)

    def record_api_latency(self, api_name: str, latency: float):
        """Record API call latency."""
        if api_name not in self.api_latencies:
            self.api_latencies[api_name] = []
        self.api_latencies[api_name].append(latency)

    def record_component_timing(self, component: str, duration: float):
        """Record component execution time."""
        if component not in self.component_timings:
            self.component_timings[component] = []
        self.component_timings[component].append(duration)

    def get_cycle_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for cycle durations."""
        stats = {}

        for cycle_id, timings in self.cycle_timings.items():
            if timings:
                stats[cycle_id] = {
                    "count": len(timings),
                    "mean": sum(timings) / len(timings),
                    "min": min(timings),
                    "max": max(timings)
                }

        return stats

    def get_api_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for API latencies."""
        stats = {}

        for api, latencies in self.api_latencies.items():
            if latencies:
                stats[api] = {
                    "count": len(latencies),
                    "mean": sum(latencies) / len(latencies),
                    "min": min(latencies),
                    "max": max(latencies),
                    "p50": self._percentile(latencies, 50),
                    "p95": self._percentile(latencies, 95),
                    "p99": self._percentile(latencies, 99)
                }

        return stats

    def get_component_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for component timings."""
        stats = {}

        for component, timings in self.component_timings.items():
            if timings:
                stats[component] = {
                    "count": len(timings),
                    "mean": sum(timings) / len(timings),
                    "min": min(timings),
                    "max": max(timings),
                    "total": sum(timings)
                }

        return stats

    def _percentile(self, data: List[float], p: float) -> float:
        """Calculate percentile."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    @contextmanager
    def track_component(self, component_name: str):
        """Context manager to track component execution time."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.record_component_timing(component_name, duration)

            logger.debug(
                "component_timing",
                component=component_name,
                duration_seconds=duration
            )


class AlertQualityTracker:
    """Track alert quality metrics for validation."""

    def __init__(self):
        """Initialize alert quality tracker."""
        self.alerts_generated: List[Dict] = []
        self.alert_feedback: Dict[str, Dict] = {}  # alert_id -> feedback

    def record_alert(self, alert_id: str, alert_data: Dict):
        """Record an alert being generated."""
        self.alerts_generated.append({
            "alert_id": alert_id,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": alert_data.get("severity"),
            "confidence": alert_data.get("confidence"),
            "discrepancy": alert_data.get("discrepancy"),
            "market_id": alert_data.get("market_id"),
            "news_url": str(alert_data.get("news_url"))
        })

        logger.debug("alert_recorded", alert_id=alert_id)

    def record_feedback(self, alert_id: str, was_correct: bool, actual_outcome: str | None = None):
        """Record feedback on alert accuracy (manual validation)."""
        self.alert_feedback[alert_id] = {
            "was_correct": was_correct,
            "actual_outcome": actual_outcome,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(
            "alert_feedback",
            alert_id=alert_id,
            was_correct=was_correct
        )

    def get_quality_metrics(self) -> Dict[str, any]:
        """Calculate alert quality metrics."""
        total_alerts = len(self.alerts_generated)
        feedback_count = len(self.alert_feedback)

        if feedback_count == 0:
            return {
                "total_alerts": total_alerts,
                "feedback_rate": 0.0,
                "message": "No feedback received yet"
            }

        correct_alerts = sum(1 for f in self.alert_feedback.values() if f["was_correct"])
        precision = correct_alerts / feedback_count if feedback_count > 0 else 0.0

        # Calculate confidence distribution
        confidences = [a["confidence"] for a in self.alerts_generated]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Calculate discrepancy distribution
        discrepancies = [a["discrepancy"] for a in self.alerts_generated]
        avg_discrepancy = sum(discrepancies) / len(discrepancies) if discrepancies else 0.0

        return {
            "total_alerts": total_alerts,
            "feedback_count": feedback_count,
            "feedback_rate": feedback_count / total_alerts if total_alerts > 0 else 0.0,
            "precision": precision,
            "avg_confidence": avg_confidence,
            "avg_discrepancy": avg_discrepancy,
            "by_severity": self._get_alerts_by_severity(),
            "by_confidence_level": self._get_alerts_by_confidence()
        }

    def _get_alerts_by_severity(self) -> Dict[str, int]:
        """Get alert count by severity."""
        severity_counts = {}
        for alert in self.alerts_generated:
            severity = alert.get("severity", "UNKNOWN")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts

    def _get_alerts_by_confidence(self) -> Dict[str, int]:
        """Get alert count by confidence level."""
        confidence_ranges = {
            "high (0.8+)": 0,
            "medium (0.6-0.8)": 0,
            "low (<0.6)": 0
        }

        for alert in self.alerts_generated:
            conf = alert.get("confidence", 0.0)
            if conf >= 0.8:
                confidence_ranges["high (0.8+)"] += 1
            elif conf >= 0.6:
                confidence_ranges["medium (0.6-0.8)"] += 1
            else:
                confidence_ranges["low (<0.6)"] += 1

        return confidence_ranges

    def export_feedback_data(self, output_path: str = "alert_feedback.json"):
        """Export alert feedback data for analysis."""
        import json

        data = {
            "alerts_generated": self.alerts_generated,
            "feedback": self.alert_feedback,
            "metrics": self.get_quality_metrics()
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info("alert_feedback_exported", path=output_path)

        return output_path
