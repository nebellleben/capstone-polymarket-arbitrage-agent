"""
Alert endpoints for querying and filtering arbitrage alerts.

This module provides REST endpoints for accessing alert data
with pagination, filtering, and statistics.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from src.api.models.response import (
    AlertResponse,
    AlertsListResponse,
    AlertStatsResponse,
)
from src.database.repositories import AlertRepository
from src.utils.shared_state import get_alert_store

router = APIRouter()


@router.get("/alerts", response_model=AlertsListResponse)
async def get_alerts(
    limit: int = Query(50, ge=1, le=100, description="Number of alerts to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence"),
) -> AlertsListResponse:
    """
    Get alerts with pagination and filtering.

    Query parameters allow filtering by severity and minimum confidence.
    Results are ordered by timestamp (most recent first).

    Args:
        limit: Maximum number of alerts (max 100)
        offset: Pagination offset
        severity: Filter by severity (INFO, WARNING, CRITICAL)
        min_confidence: Minimum confidence threshold

    Returns:
        AlertsListResponse with paginated alerts
    """
    alert_repo = AlertRepository()

    alerts = alert_repo.get_all(
        limit=limit,
        offset=offset,
        severity=severity,
        min_confidence=min_confidence,
    )

    total = alert_repo.count()

    # Convert ORM objects to response models
    alert_responses = [
        AlertResponse(
            id=alert.id,
            opportunity_id=alert.opportunity_id,
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            news_url=alert.news_url,
            news_title=alert.news_title,
            market_id=alert.market_id,
            market_question=alert.market_question,
            reasoning=alert.reasoning,
            confidence=alert.confidence,
            current_price=alert.current_price,
            expected_price=alert.expected_price,
            discrepancy=alert.discrepancy,
            recommended_action=alert.recommended_action,
            timestamp=alert.timestamp,
        )
        for alert in alerts
    ]

    return AlertsListResponse(
        total=total,
        limit=limit,
        offset=offset,
        alerts=alert_responses,
    )


@router.get("/alerts/recent", response_model=List[AlertResponse])
async def get_recent_alerts(
    limit: int = Query(10, ge=1, le=100, description="Number of alerts to return"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
) -> List[AlertResponse]:
    """
    Get most recent alerts.

    Returns the most recent alerts with optional severity filtering.

    Args:
        limit: Maximum number of alerts to return
        severity: Optional severity filter

    Returns:
        List of AlertResponse objects
    """
    alert_repo = AlertRepository()

    alerts = alert_repo.get_recent(limit=limit, severity=severity)

    # Convert ORM objects to response models
    alert_responses = [
        AlertResponse(
            id=alert.id,
            opportunity_id=alert.opportunity_id,
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            news_url=alert.news_url,
            news_title=alert.news_title,
            market_id=alert.market_id,
            market_question=alert.market_question,
            reasoning=alert.reasoning,
            confidence=alert.confidence,
            current_price=alert.current_price,
            expected_price=alert.expected_price,
            discrepancy=alert.discrepancy,
            recommended_action=alert.recommended_action,
            timestamp=alert.timestamp,
        )
        for alert in alerts
    ]

    return alert_responses


@router.get("/alerts/history", response_model=AlertsListResponse)
async def get_alerts_history(
    limit: int = Query(50, ge=1, le=200, description="Number of alerts to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence"),
    max_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum confidence"),
    start_date: Optional[datetime] = Query(None, description="Filter alerts after this time"),
    end_date: Optional[datetime] = Query(None, description="Filter alerts before this time"),
    market_id: Optional[str] = Query(None, description="Filter by market ID"),
    search_query: Optional[str] = Query(None, description="Full-text search query"),
    sort_by: str = Query("timestamp", description="Field to sort by (timestamp, confidence, discrepancy)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)")
) -> AlertsListResponse:
    """
    Get alert history with comprehensive filtering and search.

    Supports full-text search across title, message, reasoning, news_title, and market_question.
    Allows filtering by severity, confidence range, date range, and market ID.
    Results are paginated and sortable.

    Args:
        limit: Maximum number of alerts (max 200)
        offset: Pagination offset
        severity: Filter by severity (INFO, WARNING, CRITICAL)
        min_confidence: Minimum confidence threshold
        max_confidence: Maximum confidence threshold
        start_date: Filter alerts after this datetime
        end_date: Filter alerts before this datetime
        market_id: Filter by market ID
        search_query: Full-text search across multiple fields
        sort_by: Field to sort by (timestamp, confidence, discrepancy)
        sort_order: Sort order (asc, desc)

    Returns:
        AlertsListResponse with paginated alerts and total count
    """
    alert_repo = AlertRepository()

    # Get alerts matching search criteria
    alerts = alert_repo.search_alerts(
        search_query=search_query,
        severity=severity,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        start_time=start_date,
        end_time=end_date,
        market_id=market_id,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )

    # Get total count matching filters
    total = alert_repo.count_search_results(
        search_query=search_query,
        severity=severity,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        start_time=start_date,
        end_time=end_date,
        market_id=market_id
    )

    # Convert ORM objects to response models
    alert_responses = [
        AlertResponse(
            id=alert.id,
            opportunity_id=alert.opportunity_id,
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            news_url=alert.news_url,
            news_title=alert.news_title,
            market_id=alert.market_id,
            market_question=alert.market_question,
            reasoning=alert.reasoning,
            confidence=alert.confidence,
            current_price=alert.current_price,
            expected_price=alert.expected_price,
            discrepancy=alert.discrepancy,
            recommended_action=alert.recommended_action,
            timestamp=alert.timestamp,
        )
        for alert in alerts
    ]

    return AlertsListResponse(
        total=total,
        limit=limit,
        offset=offset,
        alerts=alert_responses,
    )


@router.get("/alerts/timeline")
async def get_timeline_data(
    interval: str = Query("hour", description="Time grouping interval (hour, day, week)"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence")
) -> dict:
    """
    Get alerts aggregated by time intervals for timeline view.

    Groups alerts by hour/day/week with counts and severity breakdown.
    Returns sample alerts for each time period.

    Args:
        interval: Time grouping (hour, day, week)
        hours: Number of hours to look back (1-168, max 7 days)
        severity: Filter by severity
        min_confidence: Minimum confidence level

    Returns:
        Dictionary with aggregated timeline data
    """
    alert_repo = AlertRepository()

    timeline_data = alert_repo.get_timeline_aggregation(
        interval=interval,
        hours=hours,
        severity=severity,
        min_confidence=min_confidence
    )

    # Convert sample alert ORM objects to response models
    for group in timeline_data["groups"]:
        sample_alerts = []
        for alert in group["sample_alerts"]:
            sample_alerts.append(AlertResponse(
                id=alert.id,
                opportunity_id=alert.opportunity_id,
                severity=alert.severity,
                title=alert.title,
                message=alert.message,
                news_url=alert.news_url,
                news_title=alert.news_title,
                market_id=alert.market_id,
                market_question=alert.market_question,
                reasoning=alert.reasoning,
                confidence=alert.confidence,
                current_price=alert.current_price,
                expected_price=alert.expected_price,
                discrepancy=alert.discrepancy,
                recommended_action=alert.recommended_action,
                timestamp=alert.timestamp,
            ))
        group["sample_alerts"] = sample_alerts

    return timeline_data


@router.get("/alerts/price-trends")
async def get_price_trends(
    market_id: str = Query(..., description="Market ID to fetch price trends for"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    interval: str = Query("hour", description="Aggregation interval (hour, day)")
) -> dict:
    """
    Get price trend history for a specific market.

    Returns current and expected prices over time, showing how
    prices have changed for each alert generated for this market.

    Args:
        market_id: Market identifier
        hours: Number of hours to look back (1-168, max 7 days)
        interval: Aggregation interval (hour, day)

    Returns:
        Dictionary with price history data points
    """
    from datetime import timedelta

    alert_repo = AlertRepository()

    # Calculate start time
    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Get all alerts for this market in the time range
    alerts = alert_repo.search_alerts(
        market_id=market_id,
        start_time=start_time,
        sort_by="timestamp",
        sort_order="asc"
    )

    # Group alerts by time interval and calculate price points
    data_points = []
    time_groups = {}

    for alert in alerts:
        # Determine time bucket
        if interval == "hour":
            bucket = alert.timestamp.strftime("%Y-%m-%d %H:00")
        elif interval == "day":
            bucket = alert.timestamp.strftime("%Y-%m-%d")
        else:
            bucket = alert.timestamp.strftime("%Y-%m-%d %H:00")

        if bucket not in time_groups:
            time_groups[bucket] = {
                "timestamp": bucket,
                "current_prices": [],
                "expected_prices": [],
                "discrepancies": []
            }

        time_groups[bucket]["current_prices"].append(alert.current_price)
        time_groups[bucket]["expected_prices"].append(alert.expected_price)
        time_groups[bucket]["discrepancies"].append(alert.discrepancy)

    # Calculate averages for each time bucket
    for bucket in sorted(time_groups.keys()):
        group = time_groups[bucket]
        data_points.append({
            "timestamp": bucket,
            "current_price": sum(group["current_prices"]) / len(group["current_prices"]),
            "expected_price": sum(group["expected_prices"]) / len(group["expected_prices"]),
            "discrepancy": sum(group["discrepancies"]) / len(group["discrepancies"]),
            "alert_count": len(group["current_prices"])
        })

    # Get market details from first alert
    market_question = alerts[0].market_question if alerts else ""

    return {
        "market_id": market_id,
        "market_question": market_question,
        "interval": interval,
        "start_time": start_time.isoformat(),
        "end_time": datetime.utcnow().isoformat(),
        "data_points": data_points
    }


@router.get("/alerts/stats", response_model=AlertStatsResponse)
async def get_alert_stats() -> AlertStatsResponse:
    """
    Get alert statistics.

    Returns aggregated statistics about alerts including
    counts by severity, average confidence, and recent activity.

    Returns:
        AlertStatsResponse with statistics
    """
    alert_repo = AlertRepository()
    stats = alert_repo.get_stats()

    return AlertStatsResponse(
        total_alerts=stats["total_alerts"],
        by_severity=stats["by_severity"],
        avg_confidence=stats["avg_confidence"],
        last_alert_timestamp=stats["last_alert_timestamp"],
        last_24h=stats["last_24h"],
    )


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str) -> AlertResponse:
    """
    Get a specific alert by ID.

    Args:
        alert_id: Alert identifier

    Returns:
        AlertResponse object

    Raises:
        HTTPException: If alert not found (404)
    """
    alert_repo = AlertRepository()
    alert = alert_repo.get_by_id(alert_id)

    if not alert:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    return AlertResponse(
        id=alert.id,
        opportunity_id=alert.opportunity_id,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        news_url=alert.news_url,
        news_title=alert.news_title,
        market_id=alert.market_id,
        market_question=alert.market_question,
        reasoning=alert.reasoning,
        confidence=alert.confidence,
        current_price=alert.current_price,
        expected_price=alert.expected_price,
        discrepancy=alert.discrepancy,
        recommended_action=alert.recommended_action,
        timestamp=alert.timestamp,
    )
