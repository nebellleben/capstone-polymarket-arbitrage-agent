"""
Metrics endpoints for querying system performance data.

This module provides endpoints for accessing cycle metrics,
performance statistics, and aggregated data.
"""

from typing import List

from fastapi import APIRouter, Query

from src.api.models.response import (
    CycleMetricResponse,
    MetricsResponse,
    PerformanceResponse,
)
from src.database.repositories import MetricsRepository

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    cycles: int = Query(10, ge=1, le=100, description="Number of cycles to aggregate"),
) -> MetricsResponse:
    """
    Get aggregated metrics for recent cycles.

    Aggregates performance data from the specified number of
    most recent detection cycles.

    Args:
        cycles: Number of recent cycles to aggregate

    Returns:
        MetricsResponse with aggregated data
    """
    metrics_repo = MetricsRepository()
    aggregated = metrics_repo.get_aggregated(cycles=cycles)

    return MetricsResponse(
        period=aggregated["period"],
        performance=aggregated["performance"],
        api_usage=aggregated["api_usage"],
        opportunities=aggregated["opportunities"],
        alerts=aggregated["alerts"],
    )


@router.get("/metrics/cycles", response_model=List[CycleMetricResponse])
async def get_cycles(
    limit: int = Query(20, ge=1, le=100, description="Number of cycles to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> List[CycleMetricResponse]:
    """
    Get cycle history with pagination.

    Returns the most recent detection cycles with full metrics.

    Args:
        limit: Maximum number of cycles to return
        offset: Pagination offset

    Returns:
        List of CycleMetricResponse objects
    """
    metrics_repo = MetricsRepository()

    # Get recent cycles (offset handling would require more complex query)
    cycles = metrics_repo.get_recent(limit=limit)

    # Convert ORM objects to response models
    cycle_responses = [
        CycleMetricResponse(
            cycle_id=cycle.cycle_id,
            start_time=cycle.start_time,
            end_time=cycle.end_time,
            duration_seconds=cycle.duration_seconds,
            news_articles_fetched=cycle.news_articles_fetched,
            news_articles_new=cycle.news_articles_new,
            markets_fetched=cycle.markets_fetched,
            markets_with_prices=cycle.markets_with_prices,
            impacts_analyzed=cycle.impacts_analyzed,
            impacts_significant=cycle.impacts_significant,
            reasoning_time_total=cycle.reasoning_time_total,
            opportunities_detected=cycle.opportunities_detected,
            opportunities_high_confidence=cycle.opportunities_high_confidence,
            alerts_generated=cycle.alerts_generated,
            error_count=cycle.error_count,
            news_to_alert_rate=cycle.news_to_alert_rate,
            opportunity_detection_rate=cycle.opportunity_detection_rate,
        )
        for cycle in cycles
    ]

    return cycle_responses


@router.get("/metrics/cycles/{cycle_id}", response_model=CycleMetricResponse)
async def get_cycle(cycle_id: str) -> CycleMetricResponse:
    """
    Get specific cycle metrics by ID.

    Args:
        cycle_id: Cycle identifier

    Returns:
        CycleMetricResponse object

    Raises:
        HTTPException: If cycle not found (404)
    """
    metrics_repo = MetricsRepository()
    cycle = metrics_repo.get_by_id(cycle_id)

    if not cycle:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Cycle {cycle_id} not found")

    return CycleMetricResponse(
        cycle_id=cycle.cycle_id,
        start_time=cycle.start_time,
        end_time=cycle.end_time,
        duration_seconds=cycle.duration_seconds,
        news_articles_fetched=cycle.news_articles_fetched,
        news_articles_new=cycle.news_articles_new,
        markets_fetched=cycle.markets_fetched,
        markets_with_prices=cycle.markets_with_prices,
        impacts_analyzed=cycle.impacts_analyzed,
        impacts_significant=cycle.impacts_significant,
        reasoning_time_total=cycle.reasoning_time_total,
        opportunities_detected=cycle.opportunities_detected,
        opportunities_high_confidence=cycle.opportunities_high_confidence,
        alerts_generated=cycle.alerts_generated,
        error_count=cycle.error_count,
        news_to_alert_rate=cycle.news_to_alert_rate,
        opportunity_detection_rate=cycle.opportunity_detection_rate,
    )


@router.get("/metrics/performance", response_model=PerformanceResponse)
async def get_performance() -> PerformanceResponse:
    """
    Get performance metrics for all cycles.

    Returns overall performance statistics including cycle
    durations, opportunity counts, and alert counts.

    Returns:
        PerformanceResponse with statistics
    """
    metrics_repo = MetricsRepository()
    performance = metrics_repo.get_performance_metrics()

    return PerformanceResponse(
        total_cycles=performance["total_cycles"],
        avg_duration_seconds=performance["avg_duration_seconds"],
        min_duration_seconds=performance["min_duration_seconds"],
        max_duration_seconds=performance["max_duration_seconds"],
        total_opportunities=performance["total_opportunities"],
        total_alerts=performance["total_alerts"],
    )
