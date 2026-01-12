#!/usr/bin/env python3
"""
Metrics Analysis Script

Generate reports and visualizations from collected metrics.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd


def load_metrics(metrics_file: str = "metrics.jsonl") -> List[Dict]:
    """Load metrics from JSONL file."""
    metrics = []

    try:
        with open(metrics_file, "r") as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))
    except FileNotFoundError:
        print(f"No metrics file found at {metrics_file}")
        return []

    return metrics


def generate_performance_report(metrics: List[Dict]) -> Dict[str, Any]:
    """Generate performance analysis report."""
    if not metrics:
        return {"error": "No metrics to analyze"}

    df = pd.DataFrame(metrics)

    report = {
        "summary": {
            "total_cycles": len(df),
            "date_range": {
                "start": df["start_time"].min(),
                "end": df["end_time"].max()
            },
            "total_duration_hours": df["duration_seconds"].sum() / 3600
        },
        "performance": {
            "avg_cycle_duration": df["duration_seconds"].mean(),
            "min_cycle_duration": df["duration_seconds"].min(),
            "max_cycle_duration": df["duration_seconds"].max(),
            "std_cycle_duration": df["duration_seconds"].std()
        },
        "opportunities": {
            "total_detected": df["opportunities_detected"].sum(),
            "avg_per_cycle": df["opportunities_detected"].mean(),
            "max_per_cycle": df["opportunities_detected"].max(),
            "cycles_with_opportunities": (df["opportunities_detected"] > 0).sum()
        },
        "alerts": {
            "total_generated": df["alerts_generated"].sum(),
            "avg_per_cycle": df["alerts_generated"].mean(),
            "severity_breakdown": aggregate_severity_counts(df)
        },
        "success_rate": {
            "opportunities_per_news": df["opportunities_detected"].sum() / max(df["news_articles_fetched"].sum(), 1),
            "alerts_per_impact": df["opportunities_detected"].sum() / max(df["impacts_analyzed"].sum(), 1)
        },
        "api_usage": aggregate_api_calls(df),
        "errors": {
            "total_errors": df["error_count"].sum(),
            "cycles_with_errors": (df["error_count"] > 0).sum(),
            "error_rate": df["error_count"].sum() / max(len(df), 1)
        }
    }

    return report


def aggregate_severity_counts(df: pd.DataFrame) -> Dict[str, int]:
    """Aggregate alert counts by severity."""
    severity_counts = {}

    for _, row in df.iterrows():
        alerts_by_severity = row.get("alerts_by_severity", {})
        for severity, count in alerts_by_severity.items():
            severity_counts[severity] = severity_counts.get(severity, 0) + count

    return severity_counts


def aggregate_api_calls(df: pd.DataFrame) -> Dict[str, int]:
    """Aggregate total API calls."""
    api_calls = {}

    for _, row in df.iterrows():
        calls = row.get("api_calls", {})
        for api, count in calls.items():
            api_calls[api] = api_calls.get(api, 0) + count

    return api_calls


def generate_trend_analysis(metrics: List[Dict]) -> Dict[str, Any]:
    """Analyze trends over time."""
    if len(metrics) < 2:
        return {"message": "Need at least 2 cycles for trend analysis"}

    df = pd.DataFrame(metrics)
    df["start_time"] = pd.to_datetime(df["start_time"])
    df = df.sort_values("start_time")

    # Trends over time
    trends = {
        "opportunities_trend": df["opportunities_detected"].tolist(),
        "alerts_trend": df["alerts_generated"].tolist(),
        "duration_trend": df["duration_seconds"].tolist(),
        "error_trend": df["error_count"].tolist()
    }

    # Calculate growth rates
    if len(df) >= 2:
        first_half = df[:len(df)//2]
        second_half = df[len(df)//2:]

        trends["growth"] = {
            "opportunities_growth": (
                second_half["opportunities_detected"].mean() -
                first_half["opportunities_detected"].mean()
            ),
            "alerts_growth": (
                second_half["alerts_generated"].mean() -
                first_half["alerts_generated"].mean()
            )
        }

    return trends


def print_report(report: Dict[str, Any]):
    """Print formatted report to console."""
    print("\n" + "=" * 80)
    print("POLYMARKET ARBITRAGE AGENT - METRICS REPORT")
    print("=" * 80)

    # Summary
    print("\n📊 SUMMARY")
    print("-" * 40)
    summary = report["summary"]
    print(f"Total Cycles: {summary['total_cycles']}")
    print(f"Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"Total Duration: {summary['total_duration_hours']:.2f} hours")

    # Performance
    print("\n⚡ PERFORMANCE")
    print("-" * 40)
    perf = report["performance"]
    print(f"Avg Cycle Duration: {perf['avg_cycle_duration']:.2f}s")
    print(f"Min Cycle Duration: {perf['min_cycle_duration']:.2f}s")
    print(f"Max Cycle Duration: {perf['max_cycle_duration']:.2f}s")
    print(f"Std Dev: {perf['std_cycle_duration']:.2f}s")

    # Opportunities
    print("\n🎯 OPPORTUNITIES")
    print("-" * 40)
    opps = report["opportunities"]
    print(f"Total Detected: {opps['total_detected']}")
    print(f"Avg Per Cycle: {opps['avg_per_cycle']:.2f}")
    print(f"Max Per Cycle: {opps['max_per_cycle']}")
    print(f"Cycles with Opportunities: {opps['cycles_with_opportunities']}")

    # Alerts
    print("\n🚨 ALERTS")
    print("-" * 40)
    alerts = report["alerts"]
    print(f"Total Generated: {alerts['total_generated']}")
    print(f"Avg Per Cycle: {alerts['avg_per_cycle']:.2f}")
    print("By Severity:")
    for severity, count in alerts.get("severity_breakdown", {}).items():
        print(f"  {severity}: {count}")

    # Success Metrics
    print("\n✅ SUCCESS RATES")
    print("-" * 40)
    success = report["success_rate"]
    print(f"Opportunities per News Article: {success['opportunities_per_news']:.3f}")
    print(f"Alerts per Impact Analyzed: {success['alerts_per_impact']:.3f}")

    # API Usage
    print("\n🔌 API USAGE")
    print("-" * 40)
    for api, count in report.get("api_usage", {}).items():
        print(f"{api}: {count} calls")

    # Errors
    print("\n❌ ERRORS")
    print("-" * 40)
    errors = report["errors"]
    print(f"Total Errors: {errors['total_errors']}")
    print(f"Cycles with Errors: {errors['cycles_with_errors']}")
    print(f"Error Rate: {errors['error_rate']:.2%}")

    print("\n" + "=" * 80)


def export_to_csv(metrics: List[Dict], output_file: str = "metrics_export.csv"):
    """Export metrics to CSV for further analysis."""
    df = pd.DataFrame(metrics)
    df.to_csv(output_file, index=False)
    print(f"\n✓ Exported metrics to {output_file}")


def main():
    """Main entry point."""
    print("Loading metrics...")

    metrics = load_metrics()

    if not metrics:
        print("No metrics found. Run the system first to generate metrics.")
        return

    print(f"Loaded {len(metrics)} cycles\n")

    # Generate reports
    report = generate_performance_report(metrics)
    print_report(report)

    # Trend analysis
    if len(metrics) >= 2:
        print("\n📈 TRENDS")
        print("-" * 40)
        trends = generate_trend_analysis(metrics)
        if "growth" in trends:
            growth = trends["growth"]
            print(f"Opportunities Growth: {growth['opportunities_growth']:+.2f} per cycle")
            print(f"Alerts Growth: {growth['alerts_growth']:+.2f} per cycle")

    # Export to CSV
    export_to_csv(metrics)

    # Save report as JSON
    report_file = f"metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✓ Saved detailed report to {report_file}")


if __name__ == "__main__":
    main()
