"""
Status and health check endpoints.

This module provides endpoints for monitoring service health
and retrieving detailed status information.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter

from src.api.models.response import HealthResponse, StatusResponse
from src.database.repositories import AlertRepository, MetricsRepository
from src.utils.shared_state import get_service_state

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for Railway monitoring.

    Returns the current health status of the service.

    Returns:
        HealthResponse with service status
    """
    service_state = get_service_state()

    return HealthResponse(
        status="healthy" if service_state.is_healthy() else "unhealthy",
        timestamp=datetime.utcnow(),
        worker_running=service_state._worker_running,
        web_server_running=service_state._web_server_running,
    )


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """
    Get detailed service status.

    Returns comprehensive status information including uptime,
    worker state, database statistics, and memory usage.

    Returns:
        StatusResponse with detailed status
    """
    service_state = get_service_state()
    status_info = service_state.get_status()

    # Get database statistics
    alert_repo = AlertRepository()
    metrics_repo = MetricsRepository()

    total_alerts = alert_repo.count()
    total_cycles = metrics_repo.count()

    status_response = StatusResponse(
        uptime_seconds=status_info["uptime_seconds"],
        worker={
            "status": "running" if status_info["worker_running"] else "stopped",
            "current_cycle": status_info["current_cycle"],
            "last_cycle_time": status_info["last_cycle_time"],
        },
        database={
            "status": "connected",
            "total_alerts": total_alerts,
            "total_cycles": total_cycles,
        },
        version="1.0.0",
    )

    return status_response
