"""
FastAPI web server for arbitrage detection monitoring.

This package provides REST API endpoints and WebSocket support
for monitoring the arbitrage detection system.
"""

from src.api.main import app

__all__ = ["app"]
