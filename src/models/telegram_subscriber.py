"""Telegram subscriber model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TelegramSubscriber(BaseModel):
    """Telegram bot subscriber."""

    chat_id: str = Field(..., description="Telegram chat ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    subscribed_at: datetime = Field(default_factory=datetime.utcnow, description="Subscription timestamp")
    is_active: bool = Field(True, description="Whether subscription is active")

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TelegramSubscriberCreate(BaseModel):
    """Request model for creating a subscriber."""

    chat_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramSubscriberResponse(BaseModel):
    """Response model for subscriber info."""

    chat_id: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    subscribed_at: datetime
    is_active: bool
