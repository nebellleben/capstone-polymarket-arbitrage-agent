"""Metrics collection and tracking for the arbitrage detection system."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from pathlib import Path
import json

import structlog

logger = structlog.get_logger()


@dataclass
class CycleMetrics:
    """Metrics for a single detection cycle."""

    cycle_id: str
    start_time: datetime
    end_time: datetime | None = None

    # Input metrics
    news_articles_fetched: int = 0
    news_articles_new: int = 0
    markets_fetched: int = 0
    markets_with_prices: int = 0

    # Processing metrics
    impacts_analyzed: int = 0
    impacts_significant: int = 0
    reasoning_time_total: float = 0.0

    # Output metrics
    opportunities_detected: int = 0
    opportunities_high_confidence: int = 0
    alerts_generated: int = 0
    alerts_by_severity: Dict[str, int] = field(default_factory=dict)

    # Performance metrics
    api_calls: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Total cycle duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def news_to_alert_rate(self) -> float:
        """Conversion rate from news articles to alerts."""
        if self.news_articles_fetched > 0:
            return self.alerts_generated / self.news_articles_fetched
        return 0.0

    @property
    def opportunity_detection_rate(self) -> float:
        """Opportunities per impact analyzed."""
        if self.impacts_analyzed > 0:
            return self.opportunities_detected / self.impacts_analyzed
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "cycle_id": self.cycle_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "news_articles_fetched": self.news_articles_fetched,
            "news_articles_new": self.news_articles_new,
            "markets_fetched": self.markets_fetched,
            "markets_with_prices": self.markets_with_prices,
            "impacts_analyzed": self.impacts_analyzed,
            "impacts_significant": self.impacts_significant,
            "reasoning_time_total": self.reasoning_time_total,
            "opportunities_detected": self.opportunities_detected,
            "opportunities_high_confidence": self.opportunities_high_confidence,
            "alerts_generated": self.alerts_generated,
            "alerts_by_severity": self.alerts_by_severity,
            "api_calls": self.api_calls,
            "error_count": len(self.errors),
            "news_to_alert_rate": self.news_to_alert_rate,
            "opportunity_detection_rate": self.opportunity_detection_rate
        }


class MetricsCollector:
    """Collect and aggregate metrics across detection cycles."""

    def __init__(self, export_path: Path | None = None):
        """Initialize metrics collector."""
        self.export_path = export_path or Path("metrics.jsonl")
        self.current_cycle: CycleMetrics | None = None
        self.cycle_history: List[CycleMetrics] = []

    def start_cycle(self, cycle_id: str) -> CycleMetrics:
        """Start a new detection cycle."""
        self.current_cycle = CycleMetrics(
            cycle_id=cycle_id,
            start_time=datetime.utcnow()
        )

        logger.info("cycle_started", cycle_id=cycle_id)

        return self.current_cycle

    def end_cycle(self) -> CycleMetrics:
        """End the current detection cycle."""
        if self.current_cycle:
            self.current_cycle.end_time = datetime.utcnow()

            # Add to history
            self.cycle_history.append(self.current_cycle)

            # Export metrics
            self._export_cycle(self.current_cycle)

            logger.info(
                "cycle_completed",
                cycle_id=self.current_cycle.cycle_id,
                duration=self.current_cycle.duration_seconds,
                opportunities=self.current_cycle.opportunities_detected,
                alerts=self.current_cycle.alerts_generated
            )

            return self.current_cycle

        raise ValueError("No active cycle to end")

    def track_api_call(self, api_name: str, count: int = 1):
        """Track an API call."""
        if self.current_cycle:
            self.current_cycle.api_calls[api_name] = \
                self.current_cycle.api_calls.get(api_name, 0) + count

    def track_error(self, error: str):
        """Track an error."""
        if self.current_cycle:
            self.current_cycle.errors.append(error)

    def get_aggregate_metrics(self, cycles: int = 10) -> Dict[str, Any]:
        """Get aggregated metrics over recent cycles."""
        recent_cycles = self.cycle_history[-cycles:] if self.cycle_history else []

        if not recent_cycles:
            return {"message": "No cycles completed yet"}

        total_duration = sum(c.duration_seconds for c in recent_cycles)
        total_opportunities = sum(c.opportunities_detected for c in recent_cycles)
        total_alerts = sum(c.alerts_generated for c in recent_cycles)
        total_errors = sum(len(c.errors) for c in recent_cycles)

        api_calls = {}
        for cycle in recent_cycles:
            for api, count in cycle.api_calls.items():
                api_calls[api] = api_calls.get(api, 0) + count

        return {
            "period": {
                "cycles_analyzed": len(recent_cycles),
                "duration_hours": total_duration / 3600,
            },
            "performance": {
                "avg_cycle_duration_seconds": total_duration / len(recent_cycles),
                "avg_opportunities_per_cycle": total_opportunities / len(recent_cycles),
                "avg_alerts_per_cycle": total_alerts / len(recent_cycles),
                "total_errors": total_errors,
                "error_rate": total_errors / len(recent_cycles)
            },
            "api_usage": api_calls,
            "opportunities": {
                "total_detected": total_opportunities,
                "by_cycle": [c.opportunities_detected for c in recent_cycles]
            },
            "alerts": {
                "total_generated": total_alerts,
                "by_cycle": [c.alerts_generated for c in recent_cycles],
                "by_severity": self._aggregate_alert_severity(recent_cycles)
            }
        }

    def _aggregate_alert_severity(self, cycles: List[CycleMetrics]) -> Dict[str, int]:
        """Aggregate alerts by severity across cycles."""
        severity_counts: Dict[str, int] = {}

        for cycle in cycles:
            for severity, count in cycle.alerts_by_severity.items():
                severity_counts[severity] = severity_counts.get(severity, 0) + count

        return severity_counts

    def _export_cycle(self, cycle: CycleMetrics):
        """Export cycle metrics to JSONL file."""
        try:
            with open(self.export_path, "a") as f:
                f.write(json.dumps(cycle.to_dict()) + "\n")
        except Exception as e:
            logger.error("metrics_export_failed", error=str(e))

    def export_summary(self, output_path: Path | None = None):
        """Export aggregated metrics summary to JSON."""
        path = output_path or Path("metrics_summary.json")

        summary = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_cycles": len(self.cycle_history),
            "aggregates_last_10_cycles": self.get_aggregate_metrics(10),
            "aggregates_all_time": self.get_aggregate_metrics(len(self.cycle_history))
        }

        with open(path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info("metrics_summary_exported", path=str(path))

        return path


class Timer:
    """Context manager for timing operations."""

    def __init__(self, name: str, metrics_collector: MetricsCollector | None = None):
        """Initialize timer."""
        self.name = name
        self.metrics = metrics_collector
        self.start_time = 0.0
        self.end_time = 0.0

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log."""
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        logger.debug(
            "timer",
            name=self.name,
            duration_seconds=duration
        )

        if self.metrics and self.metrics.current_cycle:
            # Store timing in appropriate metric
            if "reasoning" in self.name.lower():
                self.metrics.current_cycle.reasoning_time_total += duration


def track_performance(func):
    """Decorator to track function performance."""
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start
            logger.debug(
                "function_performance",
                function=func.__name__,
                duration_seconds=duration
            )
    return wrapper
