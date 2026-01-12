"""
FastAPI application for arbitrage detection monitoring.

This module sets up the FastAPI application with CORS middleware,
exception handlers, and route registration.
"""

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Lazy imports to avoid blocking startup
# from src.api.models.response import ErrorResponse, HealthResponse
# from src.utils.logging_config import logger
# from src.utils.shared_state import get_service_state


# Create FastAPI application
app = FastAPI(
    title="Polymarket Arbitrage Agent API",
    description="Monitoring API for arbitrage detection system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Include routers (lazy import to avoid blocking startup)
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Lazy import dependencies
    from src.utils.logging_config import logger
    from src.utils.shared_state import get_service_state

    logger.info("api_startup")

    # Set web server running status
    service_state = get_service_state()
    service_state.set_web_server_running(True)

    # Include routers (lazy import to avoid blocking startup)
    from src.api.routes import alerts, metrics, status

    app.include_router(alerts.router, prefix="/api", tags=["alerts"])
    app.include_router(metrics.router, prefix="/api", tags=["metrics"])
    app.include_router(status.router, prefix="/api", tags=["status"])

    logger.info("routers_included")

    # Note: Database is initialized by the entrypoint script before startup
    # We don't initialize it here to avoid blocking the web server startup


# Exception handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("api_startup")

    # Set web server running status
    service_state = get_service_state()
    service_state.set_web_server_running(True)

    # Note: Database is initialized by the entrypoint script before startup
    # We don't initialize it here to avoid blocking the web server startup


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("api_shutdown")

    # Set web server running status
    service_state = get_service_state()
    service_state.set_web_server_running(False)

    # Close database connection
    try:
        from src.database.connection import get_db
        get_db().close()
        logger.info("database_closed")
    except Exception as e:
        logger.error("database_close_failed", error=str(e))


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "Polymarket Arbitrage Agent API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }


# Static file serving (for dashboard)
import os
from pathlib import Path

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    from fastapi.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info("static_files_mounted", path=str(static_dir))
