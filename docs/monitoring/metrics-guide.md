# Monitoring and Metrics Guide

## Overview

This document explains how to use the monitoring and metrics collection system for the Polymarket Arbitrage Agent MVP.

## Metrics Collection

### Automatic Collection

The system automatically collects metrics during operation:

1. **Cycle Metrics**: Tracked for each detection cycle
   - News articles fetched and processed
   - Markets retrieved and analyzed
   - Impacts computed
   - Opportunities detected
   - Alerts generated

2. **API Metrics**: External API calls
   - Brave Search API calls
   - Polymarket Gamma API calls
   - Anthropic API calls (reasoning)

3. **Performance Metrics**
   - Detection cycle duration
   - API call latencies
   - Component execution times

4. **Quality Metrics**
   - Alert accuracy (with feedback)
   - Confidence distribution
   - False positive rate

### Metrics Files

**JSONL Format** (`metrics.jsonl`):
```
{"cycle_id":"cycle-001","start_time":"2025-01-12T10:00:00","news_articles_fetched":10,...}
{"cycle_id":"cycle-002","start_time":"2025-01-12T10:01:00","news_articles_fetched":10,...}
```

**Summary JSON** (`metrics_summary.json`):
```json
{
  "generated_at": "2025-01-12T10:00:00",
  "total_cycles": 10,
  "aggregates_last_10_cycles": {...}
}
```

## Key Performance Indicators (KPIs)

### Success Metrics (from PRD)

| KPI | Target | How to Measure |
|-----|--------|----------------|
| News Processing Latency | < 30s | Cycle duration / news count |
| Detection Accuracy | > 70% | Alert precision (from feedback) |
| False Positive Rate | < 30% | 1 - precision |
| System Availability | > 95% | Uptime monitoring |
| Daily Opportunities | 5-10 | Sum of opportunities per day |

### Operational Metrics

| Metric | Description | Good Range |
|--------|-------------|-------------|
| Avg Cycle Duration | Time per detection cycle | 30-90s |
| API Call Rate | Calls per second | < 10 (Polymarket limit) |
| Error Rate | Cycles with errors | < 5% |
| Alert Rate | Alerts per cycle | 0.1-1.0 |
| Opportunity Rate | Opportunities per cycle | 0.05-0.5 |

## Using Metrics

### View Real-time Metrics

```bash
# Run the system (metrics collected automatically)
python -m src.workflows.mvp_workflow

# Metrics are written to metrics.jsonl
```

### Generate Reports

```bash
# Analyze collected metrics
python scripts/analyze-metrics.py

# This will:
# - Load metrics.jsonl
# - Calculate statistics
# - Print formatted report
# - Export to CSV
# - Save JSON report
```

### Export Metrics for Analysis

```python
from src.utils.metrics import MetricsCollector

collector = MetricsCollector()

# Get aggregated metrics
aggregates = collector.get_aggregate_metrics(cycles=10)

# Export summary
collector.export_summary("my_metrics_summary.json")
```

## Alert Quality Tracking

### Recording Feedback

After deployment, you'll want to track alert quality:

```python
from src.utils.performance import AlertQualityTracker

tracker = AlertQualityTracker()

# Generate an alert (automatic)
tracker.record_alert(
    alert_id="alert-001",
    alert_data={
        "severity": "WARNING",
        "confidence": 0.75,
        "discrepancy": 0.10,
        "market_id": "market-123",
        "news_url": "https://example.com/news1"
    }
)

# Record feedback (manual validation)
tracker.record_feedback(
    alert_id="alert-001",
    was_correct=True,  # Did the opportunity actually materialize?
    actual_outcome="Price moved up as predicted"
)

# Export quality metrics
tracker.export_feedback_data("alert_quality.json")
```

### Quality Metrics

**Precision**: % of alerts that were correct
```
Precision = Correct Alerts / Total Alerts with Feedback
```

**Confidence Calibration**: Are high-confidence alerts more accurate?
```
Analyze confidence vs. correctness correlation
```

## Performance Monitoring

### Track API Latency

```python
from src.utils.performance import PerformanceTracker

tracker = PerformanceTracker()

# API latencies are tracked automatically
stats = tracker.get_api_stats()

print(f"Brave Search latency: {stats['brave_search']['mean']:.2f}s")
print(f"Polymarket latency: {stats['polymarket_gamma']['mean']:.2f}s")
```

### Track Component Performance

```python
# Get component timing stats
stats = tracker.get_component_stats()

for component, timings in stats.items():
    print(f"{component}:")
    print(f"  Average: {timings['mean']:.2f}s")
    print(f"  Total: {timings['total']:.2f}s")
```

## Setting Up Monitoring Dashboard

### Option 1: Simple Text Dashboard

The `analyze-metrics.py` script provides a text-based dashboard:

```bash
python scripts/analyze-metrics.py
```

Output:
```
================================================================================
POLYMARKET ARBITRAGE AGENT - METRICS REPORT
================================================================================

📊 SUMMARY
----------------------------------------
Total Cycles: 10
Date Range: 2025-01-12T10:00:00 to 2025-01-12T10:10:00
Total Duration: 0.15 hours

⚡ PERFORMANCE
----------------------------------------
Avg Cycle Duration: 45.23s
Min Cycle Duration: 38.12s
Max Cycle Duration: 62.45s
Std Dev: 8.34s
...
```

### Option 2: Export to External Tools

Metrics are exported in formats compatible with:

1. **Grafana + Prometheus** (Future)
   - Set up Prometheus to scrape metrics endpoint
   - Create Grafana dashboards

2. **Google Sheets** (Quick & Easy)
   - Export to CSV
   - Import to Google Sheets
   - Use built-in charts

3. **Jupyter Notebooks** (Analysis)
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt

   # Load metrics
   df = pd.read_json('metrics.jsonl', lines=True)

   # Plot opportunities over time
   df.plot(x='start_time', y='opportunities_detected')
   plt.show()
   ```

## Validation and Optimization

### Validate Requirements

Use metrics to validate PRD requirements:

```python
# Load report
with open('metrics_summary.json') as f:
    report = json.load(f)

# Check targets
daily_opportunities = report['aggregates_all_time']['opportunities']['total_detected']
cycles_per_day = report['aggregates_all_time']['period']['cycles_analyzed']
opportunities_per_cycle = daily_opportunities / cycles_per_day

print(f"Opportunities per cycle: {opportunities_per_cycle:.2f}")
print(f"Target: 5-10 per day")

if 5 <= opportunities_per_cycle <= 10:
    print("✅ Meeting target!")
else:
    print("⚠️  Outside target range")
```

### Optimize Performance

Identify bottlenecks:

```bash
# Run analysis
python scripts/analyze-metrics.py

# Check component timings
# If "reasoning" component is slow:
# - Consider reducing news_market pairs analyzed
# - Lower RELEVANCE_THRESHOLD
# - Use faster model

# If "fetch_markets" is slow:
# - Reduce MARKET_REFRESH_INTERVAL
# - Limit number of markets fetched
```

### Optimize Alert Quality

Track precision over time:

1. **Week 1**: Collect baseline metrics
2. **Week 2**: Adjust `CONFIDENCE_THRESHOLD`
3. **Week 3**: Measure improvement
4. **Iterate**

```python
# Load feedback data
with open('alert_quality.json') as f:
    data = json.load(f)

# Calculate precision
precision = data['metrics']['precision']
print(f"Current precision: {precision:.1%}")

# If precision < 70%:
# - Increase CONFIDENCE_THRESHOLD
# - Increase MIN_PROFIT_MARGIN
# - Improve reasoning prompts
```

## Monitoring Alerts

### Set Up Alerts

Based on metrics, set up alerts for:

1. **High Error Rate**: > 10% cycles have errors
   ```python
   if report["errors"]["error_rate"] > 0.1:
       alert("High error rate detected!")
   ```

2. **No Opportunities**: 24 hours without opportunities
   ```python
   if report["opportunities"]["total_detected"] == 0:
       alert("No opportunities detected in 24h")
   ```

3. **API Rate Limits**: Exceeding rate limits
   ```python
   if api_stats["polymarket_gamma"]["p95"] > 1.0:
       alert("API latency high - may be rate limited")
   ```

## Metrics Export Formats

### JSONL (Line-delimited JSON)
```
{"cycle_id":"1","start_time":"2025-01-12T10:00:00",...}
{"cycle_id":"2","start_time":"2025-01-12T10:01:00",...}
```
- **Use**: Streaming analysis, big data processing

### JSON Summary
```json
{
  "total_cycles": 10,
  "aggregates": {...}
}
```
- **Use**: Quick overview, dashboard display

### CSV
```
cycle_id,start_time,duration_seconds,opportunities_detected,...
```
- **Use**: Spreadsheet analysis, charting tools

## Troubleshooting

### No Metrics Generated

**Check**:
1. Is `metrics.py` being imported?
2. Is `MetricsCollector` being used?
3. Does the application have write permissions?

**Solution**:
```python
# In workflow, ensure metrics are initialized
from src.utils.metrics import MetricsCollector

self.metrics = MetricsCollector()
```

### Metrics File Empty

**Check**:
1. Are cycles completing successfully?
2. Is there a `metrics.jsonl` file?
3. Check error logs for export failures

### Inconsistent Metrics

**Check**:
1. Clock synchronization (if distributed)
2. Metric calculation logic
3. Data quality issues

## Continuous Improvement

### Weekly Review

1. Run `analyze-metrics.py`
2. Check KPIs against targets
3. Identify trends
4. Adjust thresholds

### Monthly Review

1. Deep dive into all metrics
2. A/B test different configurations
3. Update documentation
4. Report findings

---

**Last Updated**: 2025-01-12
**Maintained By**: Data Analyst Agent
