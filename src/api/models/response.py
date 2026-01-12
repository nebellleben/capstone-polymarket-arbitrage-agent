"""
Pydantic response models for API endpoints.

This module defines the response schemas for all API endpoints,
ensuring type safety and automatic validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    """Alert response model."""

    id: str = Field(..., description="Alert identifier")
    opportunity_id: str = Field(..., description="Associated opportunity ID")
    severity: str = Field(..., description="Alert severity (INFO, WARNING, CRITICAL)")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    news_url: str = Field(..., description="URL to related news article")
    news_title: str = Field(..., description="Title of news article")
    market_id: str = Field(..., description="Polymarket market ID")
    market_question: str = Field(..., description="Market question text")
    reasoning: str = Field(..., description="AI reasoning for the alert")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    current_price: float = Field(..., ge=0.0, le=1.0, description="Current market price")
    expected_price: float = Field(..., ge=0.0, le=1.0, description="Expected price")
    discrepancy: float = Field(..., description="Price discrepancy percentage")
    recommended_action: str = Field(..., description="Recommended action")
    timestamp: datetime = Field(..., description="Alert timestamp")

    model_config = {"from_attributes": True}


class AlertsListResponse(BaseModel):
    """Paginated alerts list response."""

    total: int = Field(..., description="Total number of alerts")
    limit: int = Field(..., description="Number of alerts per page")
    offset: int = Field(..., description="Pagination offset")
    alerts: List[AlertResponse] = Field(..., description="List of alerts")


class AlertStatsResponse(BaseModel):
    """Alert statistics response."""

    total_alerts: int = Field(..., description="Total number of alerts")
    by_severity: Dict[str, int] = Field(..., description="Alert counts by severity")
    avg_confidence: float = Field(..., description="Average confidence score")
    last_alert_timestamp: Optional[datetime] = Field(None, description="Most recent alert time")
    last_24h: int = Field(..., description="Number of alerts in last 24 hours")


class CycleMetricResponse(BaseModel):
    """Cycle metric response model."""

    cycle_id: str = Field(..., description="Cycle identifier")
    start_time: datetime = Field(..., description="Cycle start time")
    end_time: datetime = Field(..., description="Cycle end time")
    duration_seconds: float = Field(..., description="Cycle duration in seconds")
    news_articles_fetched: int = Field(..., description="Number of news articles fetched")
    news_articles_new: int = Field(..., description="Number of new articles")
    markets_fetched: int = Field(..., description="Number of markets fetched")
    markets_with_prices: int = Field(..., description="Markets with price data")
    impacts_analyzed: int = Field(..., description="Number of impacts analyzed")
    impacts_significant: int = Field(..., description="Number of significant impacts")
    reasoning_time_total: float = Field(..., description="Total reasoning time")
    opportunities_detected: int = Field(..., description="Opportunities found")
    opportunities_high_confidence: int = Field(..., description="High-confidence opportunities")
    alerts_generated: int = Field(..., description="Alerts generated")
    error_count: int = Field(..., description="Number of errors")
    news_to_alert_rate: float = Field(..., description="News to alert conversion rate")
    opportunity_detection_rate: float = Field(..., description="Opportunity detection rate")

    model_config = {"from_attributes": True}


class MetricsResponse(BaseModel):
    """Aggregated metrics response."""

    period: Dict[str, Any] = Field(..., description="Time period information")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
    api_usage: Dict[str, int] = Field(..., description="API call counts")
    opportunities: Dict[str, Any] = Field(..., description="Opportunity statistics")
    alerts: Dict[str, Any] = Field(..., description="Alert statistics")


class PerformanceResponse(BaseModel):
    """Performance metrics response."""

    total_cycles: int = Field(..., description="Total number of cycles")
    avg_duration_seconds: float = Field(..., description="Average cycle duration")
    min_duration_seconds: float = Field(..., description="Minimum cycle duration")
    max_duration_seconds: float = Field(..., description="Maximum cycle duration")
    total_opportunities: int = Field(..., description="Total opportunities detected")
    total_alerts: int = Field(..., description="Total alerts generated")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status (healthy/unhealthy)")
    timestamp: datetime = Field(..., description="Current timestamp")
    worker_running: bool = Field(..., description="Whether worker is running")
    web_server_running: bool = Field(..., description="Whether web server is running")


class StatusResponse(BaseModel):
    """Detailed service status response."""

    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    worker: Dict[str, Any] = Field(..., description="Worker status")
    database: Dict[str, Any] = Field(..., description="Database status")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    version: str = Field(..., description="Service version")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(..., description="Error timestamp")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: str = Field(..., description="Message type (alert_created, cycle_completed, etc.)")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(..., description="Message timestamp")
