"""
API route handlers for arbitrage detection monitoring.

This package contains all route handlers for the FastAPI application.
"""

from src.api.routes import alerts, metrics, status

__all__ = ["alerts", "metrics", "status"]
