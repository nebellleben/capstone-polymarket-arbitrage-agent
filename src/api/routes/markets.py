"""
Market endpoints for querying market-related data.

This module provides REST endpoints for accessing market performance
data including leaderboards and market-specific metrics.
"""

from typing import List, Optional

from fastapi import APIRouter, Query
from sqlalchemy import func

from src.database.repositories import AlertRepository
from src.database.connection import get_db
from src.database.models import Alert

router = APIRouter()


@router.get("/markets/leaderboard")
async def get_market_leaderboard(
    limit: int = Query(20, ge=1, le=50, description="Number of markets to return"),
    sort_by: str = Query("alert_count", description="Sort by field (alert_count, avg_discrepancy, avg_confidence)"),
    min_alerts: int = Query(3, ge=1, description="Minimum number of alerts to qualify")
) -> List[dict]:
    """
    Get market performance leaderboard.

    Returns ranked list of markets by performance metrics.
    Aggregates alert data per market including alert count, average discrepancy, and average confidence.

    Args:
        limit: Maximum number of markets to return
        sort_by: Field to sort by (alert_count, avg_discrepancy, avg_confidence)
        min_alerts: Minimum number of alerts for a market to be included

    Returns:
        List of market performance dictionaries with rankings
    """
    db = get_db().get_session().__enter__()

    # Build query to aggregate alerts by market
    query = db.query(
        Alert.market_id,
        Alert.market_question,
        func.count(Alert.id).label("alert_count"),
        func.avg(Alert.discrepancy).label("avg_discrepancy"),
        func.avg(Alert.confidence).label("avg_confidence"),
        func.max(Alert.timestamp).label("last_alert_timestamp")
    ).group_by(
        Alert.market_id,
        Alert.market_question
    ).having(
        func.count(Alert.id) >= min_alerts
    )

    # Execute query to get all market stats
    results = query.all()

    # Process results and calculate severity breakdown
    markets = []
    for result in results:
        market_id, market_question, alert_count, avg_discrepancy, avg_confidence, last_timestamp = result

        # Get severity breakdown for this market
        severity_stats = db.query(
            Alert.severity,
            func.count(Alert.id)
        ).filter(
            Alert.market_id == market_id
        ).group_by(Alert.severity).all()

        severity_breakdown = {severity: count for severity, count in severity_stats}

        # Determine trend (compare recent vs older alerts)
        recent_count = db.query(func.count(Alert.id)).filter(
            Alert.market_id == market_id,
            Alert.timestamp >= last_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        ).scalar()

        # Simple trend logic: if more alerts in last period, trend is up
        if alert_count > 0 and recent_count >= alert_count * 0.5:
            trend = "up"
        elif recent_count > 0:
            trend = "stable"
        else:
            trend = "down"

        markets.append({
            "market_id": market_id,
            "question": market_question,
            "alert_count": alert_count,
            "avg_discrepancy": round(avg_discrepancy or 0, 4),
            "avg_confidence": round(avg_confidence or 0, 4),
            "last_alert_timestamp": last_timestamp.isoformat() if last_timestamp else None,
            "severity_breakdown": {
                "CRITICAL": severity_breakdown.get("CRITICAL", 0),
                "WARNING": severity_breakdown.get("WARNING", 0),
                "INFO": severity_breakdown.get("INFO", 0)
            },
            "trend": trend
        })

    # Sort markets
    reverse_order = True  # Default to descending for all sorts
    if sort_by == "alert_count":
        markets.sort(key=lambda x: x["alert_count"], reverse=reverse_order)
    elif sort_by == "avg_discrepancy":
        markets.sort(key=lambda x: x["avg_discrepancy"], reverse=reverse_order)
    elif sort_by == "avg_confidence":
        markets.sort(key=lambda x: x["avg_confidence"], reverse=reverse_order)

    # Add rankings
    for i, market in enumerate(markets[:limit], 1):
        market["rank"] = i

    # Return top N markets
    return markets[:limit]


@router.get("/markets/{market_id}/alerts")
async def get_market_alerts(
    market_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of alerts to return")
) -> List[dict]:
    """
    Get all alerts for a specific market.

    Args:
        market_id: Market identifier
        limit: Maximum number of alerts to return

    Returns:
        List of Alert dictionaries for the specified market
    """
    from src.api.models.response import AlertResponse

    alert_repo = AlertRepository()
    alerts = alert_repo.get_alerts_by_market(market_id, limit)

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

    return [alert.dict() for alert in alert_responses]
