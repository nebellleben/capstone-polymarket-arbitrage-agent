"""Debug endpoints for troubleshooting database issues."""

from fastapi import APIRouter
from pathlib import Path
import os
import glob

from src.database.connection import get_db
from src.database.repositories import AlertRepository
from src.utils.logging_config import logger
from sqlalchemy import inspect, text

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

    # Search for ALL database files in container
    all_db_files = []
    for db_file in glob.glob("/app/**/*.db", recursive=True):
        stat = os.stat(db_file)
        all_db_files.append({
            "path": db_file,
            "size": stat.st_size,
            "modified": stat.st_mtime
        })

    # Check database schema
    tables = []
    row_counts = {}
    try:
        with db_manager.get_session() as session:
            inspector = inspect(session.bind)
            tables = inspector.get_table_names()

            # Count rows in each table
            for table in tables:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                row_counts[table] = result.scalar()

    except Exception as e:
        logger.error("debug_schema_error", error=str(e))

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
            "all_db_files": all_db_files,
            "tables": tables,
            "row_counts": row_counts,
            "total_alerts_in_db": count,
            "recent_alert_ids": alert_ids,
            "pool_class": "NullPool",
            "data_dir": os.environ.get("DATA_DIR", "not set")
        }
    except Exception as e:
        logger.error("debug_database_error", error=str(e), exc_info=True)
        return {
            "database_path": db_path,
            "file_exists": db_exists,
            "file_size_bytes": file_size,
            "all_db_files": all_db_files,
            "tables": tables,
            "row_counts": row_counts,
            "error": str(e)
        }
