"""Telegram notification routes."""

from typing import Any, List

from fastapi import APIRouter, HTTPException

from src.notifications.telegram_notifier import create_telegram_notifier
from src.models.alert import AlertSeverity
from src.models.telegram_subscriber import TelegramSubscriberResponse
from src.database.telegram_subscribers import TelegramSubscriberRepository
from src.utils.config import settings
from src.utils.logging_config import logger

router = APIRouter()


@router.get("/telegram/test")
async def send_test_notification() -> dict[str, Any]:
    """
    Send a test Telegram notification to all subscribers.

    This endpoint sends a test message to verify Telegram integration is working.

    Returns:
        Dict with success status and broadcast details
    """
    # Check if Telegram is configured
    if not settings.telegram_enabled or not settings.telegram_bot_token:
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

        # Broadcast test message to all subscribers
        result = notifier.broadcast_test_message()

        if result.get("success"):
            logger.info("telegram_test_broadcast_sent", result=result)
            return {
                "success": True,
                "message": "Test notification sent to Telegram",
                "total_subscribers": result.get("total_subscribers", 0),
                "success_count": result.get("success_count", 0),
                "failed_count": result.get("failed_count", 0),
                "details": result.get("results", [])
            }
        else:
            logger.error("telegram_test_failed", reason=result.get("reason"))
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send test notification: {result.get('reason')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("telegram_test_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error sending test notification: {str(e)}"
        )


@router.get("/telegram/status")
async def get_telegram_status() -> dict[str, Any]:
    """
    Get Telegram notification status and subscriber count.

    Returns:
        Dict with Telegram configuration status
    """
    try:
        repo = TelegramSubscriberRepository()
        subscriber_count = repo.get_subscriber_count()

        return {
            "enabled": settings.telegram_enabled,
            "configured": bool(settings.telegram_bot_token and settings.telegram_chat_id),
            "min_severity": settings.telegram_min_severity,
            "chat_id": settings.telegram_chat_id if settings.telegram_chat_id else None,
            "total_subscribers": subscriber_count
        }
    except Exception as e:
        logger.error("telegram_status_error", error=str(e))
        return {
            "enabled": settings.telegram_enabled,
            "configured": bool(settings.telegram_bot_token and settings.telegram_chat_id),
            "min_severity": settings.telegram_min_severity,
            "chat_id": settings.telegram_chat_id if settings.telegram_chat_id else None,
            "total_subscribers": 0,
            "error": str(e)
        }


@router.get("/telegram/subscribers", response_model=List[TelegramSubscriberResponse])
async def get_subscribers() -> List[TelegramSubscriberResponse]:
    """
    Get all active Telegram subscribers.

    Returns:
        List of active subscribers
    """
    try:
        repo = TelegramSubscriberRepository()
        subscribers = repo.get_all_active_subscribers()
        return [
            TelegramSubscriberResponse(
                chat_id=s.chat_id,
                username=s.username,
                first_name=s.first_name,
                last_name=s.last_name,
                subscribed_at=s.subscribed_at,
                is_active=s.is_active
            )
            for s in subscribers
        ]
    except Exception as e:
        logger.error("get_subscribers_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error getting subscribers: {str(e)}"
        )


@router.post("/telegram/subscribers/{chat_id}")
async def add_subscriber(chat_id: str) -> dict[str, Any]:
    """
    Manually add a Telegram subscriber.

    Args:
        chat_id: Telegram chat ID to add

    Returns:
        Dict with success status
    """
    try:
        repo = TelegramSubscriberRepository()
        subscriber = repo.add_subscriber(chat_id=chat_id)

        logger.info("subscriber_added", chat_id=chat_id)
        return {
            "success": True,
            "message": "Subscriber added successfully",
            "subscriber": {
                "chat_id": subscriber.chat_id,
                "username": subscriber.username,
                "first_name": subscriber.first_name,
                "last_name": subscriber.last_name
            }
        }
    except Exception as e:
        logger.error("add_subscriber_error", chat_id=chat_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error adding subscriber: {str(e)}"
        )


@router.delete("/telegram/subscribers/{chat_id}")
async def remove_subscriber(chat_id: str) -> dict[str, Any]:
    """
    Remove a Telegram subscriber (mark as inactive).

    Args:
        chat_id: Telegram chat ID to remove

    Returns:
        Dict with success status
    """
    try:
        repo = TelegramSubscriberRepository()
        success = repo.remove_subscriber(chat_id)

        if success:
            logger.info("subscriber_removed", chat_id=chat_id)
            return {
                "success": True,
                "message": "Subscriber removed successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Subscriber {chat_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("remove_subscriber_error", chat_id=chat_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error removing subscriber: {str(e)}"
        )
