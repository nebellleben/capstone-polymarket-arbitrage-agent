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

from src.utils.logging_config import logger


# Create FastAPI application
app = FastAPI(
    title="Polymarket Arbitrage Agent API",
    description="Monitoring API for arbitrage detection system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
import os as _os
_allowed_origins = _os.getenv("ALLOWED_ORIGINS", "").split(",")
if not _allowed_origins[0]:  # If empty, use localhost for development
    _allowed_origins = ["http://localhost:8080", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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
    logger.info("api_startup")

    # Set web server running status
    from src.utils.shared_state import get_service_state
    service_state = get_service_state()
    service_state.set_web_server_running(True)

    # Include routers (lazy import to avoid blocking startup)
    from src.api.routes import alerts, debug, markets, metrics, status, telegram

    app.include_router(alerts.router, prefix="/api", tags=["alerts"])
    app.include_router(debug.router, prefix="/api", tags=["debug"])
    app.include_router(markets.router, prefix="/api", tags=["markets"])
    app.include_router(metrics.router, prefix="/api", tags=["metrics"])
    app.include_router(status.router, prefix="/api", tags=["status"])
    app.include_router(telegram.router, prefix="/api", tags=["telegram"])

    logger.info("routers_included")

    # Note: Database is initialized by the entrypoint script before startup
    # We don't initialize it here to avoid blocking the web server startup


# Exception handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom HTTP exception handler with sanitized error messages."""
    # Log detailed error internally for debugging
    logger.error(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )

    # Return generic error to client (don't expose internal details)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if exc.status_code < 500 else "An error occurred",
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


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("api_shutdown")

    # Set web server running status
    from src.utils.shared_state import get_service_state
    service_state = get_service_state()
    service_state.set_web_server_running(False)

    # Close database connection
    try:
        from src.database.connection import get_db
        get_db().close()
        logger.info("database_closed")
    except Exception as e:
        logger.error("database_close_failed", error=str(e))


# Root endpoint - serve dashboard
from fastapi.responses import FileResponse
from pathlib import Path as FilePath

@app.get("/")
async def root():
    """Serve the dashboard HTML."""
    index_path = FilePath(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "Polymarket Arbitrage Agent API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }

@app.get("/api")
async def api_info() -> dict[str, str]:
    """API information endpoint."""
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
    # Note: logger not available at module level, logging done in startup
