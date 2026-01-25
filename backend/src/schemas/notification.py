from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationChannelBase(BaseModel):
    provider: str  # discord_webhook, telegram_bot, slack_webhook, line_notify, etc.
    credentials: Dict[str, Any]  # Flexible: {"url": "..."} or {"token": "...", "chat_id": "..."}
    name: Optional[str] = None
    notification_hours: Optional[list[int]] = None  # List of hours (0-23) when notifications should be sent


class NotificationChannelCreate(NotificationChannelBase):
    pass


class NotificationChannelUpdate(BaseModel):
    provider: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    notification_hours: Optional[list[int]] = None  # List of hours (0-23) when notifications should be sent


class NotificationChannelResponse(NotificationChannelBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

