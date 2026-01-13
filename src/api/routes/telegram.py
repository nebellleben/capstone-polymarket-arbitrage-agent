"""Telegram notification routes."""

from typing import Any

from fastapi import APIRouter, HTTPException

from src.notifications.telegram_notifier import create_telegram_notifier
from src.models.alert import AlertSeverity
from src.utils.config import settings
from src.utils.logging_config import logger

router = APIRouter()


@router.get("/telegram/test")
async def send_test_notification() -> dict[str, Any]:
    """
    Send a test Telegram notification.

    This endpoint sends a test message to verify Telegram integration is working.

    Returns:
        Dict with success status and message
    """
    # Check if Telegram is configured
    if not settings.telegram_enabled or not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("telegram_test_failed", reason="not_configured")
        raise HTTPException(
            status_code=503,
            detail="Telegram notifications are not configured on this server"
        )

    try:
        # Create notifier
        min_severity = AlertSeverity[settings.telegram_min_severity.upper()]
        notifier = create_telegram_notifier(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
            enabled=settings.telegram_enabled,
            min_severity=min_severity
        )

        if not notifier.is_enabled():
            logger.warning("telegram_test_failed", reason="not_enabled")
            raise HTTPException(
                status_code=503,
                detail="Telegram notifier is not enabled"
            )

        # Send test message
        success = notifier.send_test_message()

        if success:
            logger.info("telegram_test_sent", chat_id=settings.telegram_chat_id)
            return {
                "success": True,
                "message": "Test notification sent to Telegram",
                "chat_id": settings.telegram_chat_id,
                "timestamp": None  # Will be set by response
            }
        else:
            logger.error("telegram_test_failed", reason="api_error")
            raise HTTPException(
                status_code=500,
                detail="Failed to send test notification. Check server logs for details."
            )

    except Exception as e:
        logger.error("telegram_test_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error sending test notification: {str(e)}"
        )


@router.get("/telegram/status")
async def get_telegram_status() -> dict[str, Any]:
    """
    Get Telegram notification status.

    Returns:
        Dict with Telegram configuration status
    """
    return {
        "enabled": settings.telegram_enabled,
        "configured": bool(settings.telegram_bot_token and settings.telegram_chat_id),
        "min_severity": settings.telegram_min_severity,
        "chat_id": settings.telegram_chat_id if settings.telegram_chat_id else None
    }
