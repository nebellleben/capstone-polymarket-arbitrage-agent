"""Debug endpoints for troubleshooting database issues."""

from fastapi import APIRouter
from pathlib import Path
import os

from src.database.connection import get_db
from src.database.repositories import AlertRepository
from src.utils.logging_config import logger

router = APIRouter()


@router.get("/debug/database")
async def debug_database():
    """Debug database information."""
    db_manager = get_db()

    # Check database path
    db_path = db_manager._db_path
    db_exists = Path(db_path).exists()

    # Check file size
    file_size = 0
    if db_exists:
        file_size = os.path.getsize(db_path)

    # Try direct query
    try:
        alert_repo = AlertRepository()
        count = alert_repo.count()
        recent = alert_repo.get_recent(limit=5)

        # Get alert IDs
        alert_ids = [a.id for a in recent]

        return {
            "database_path": db_path,
            "file_exists": db_exists,
            "file_size_bytes": file_size,
            "total_alerts_in_db": count,
            "recent_alert_ids": alert_ids,
            "pool_class": "NullPool",
            "data_dir": os.environ.get("DATA_DIR", "not set")
        }
    except Exception as e:
        logger.error("debug_database_error", error=str(e))
        return {
            "database_path": db_path,
            "file_exists": db_exists,
            "file_size_bytes": file_size,
            "error": str(e)
        }
