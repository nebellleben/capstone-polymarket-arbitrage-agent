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
