from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from ..database.models import NotificationChannel


class NotificationRepository:
    """Repository for NotificationChannel operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, user_id: int, provider: str, credentials: Dict[str, Any], name: Optional[str] = None, notification_hours: Optional[List[int]] = None) -> NotificationChannel:
        """Create a new notification channel"""
        channel = NotificationChannel(
            user_id=user_id,
            provider=provider,
            credentials=credentials,
            name=name,
            notification_hours=notification_hours
        )
        self.session.add(channel)
        self.session.flush()
        return channel
    
    def get_by_id(self, channel_id: int) -> Optional[NotificationChannel]:
        """Get notification channel by ID"""
        return self.session.get(NotificationChannel, channel_id)
    
    def get_by_user_id(self, user_id: int, active_only: bool = False) -> List[NotificationChannel]:
        """Get all notification channels for a user"""
        stmt = select(NotificationChannel).where(NotificationChannel.user_id == user_id)
        if active_only:
            stmt = stmt.where(NotificationChannel.is_active == True)
        stmt = stmt.order_by(NotificationChannel.created_at.desc())
        return list(self.session.scalars(stmt).all())
    
    def get_by_user_and_provider(self, user_id: int, provider: str, active_only: bool = False) -> Optional[NotificationChannel]:
        """Get notification channel by user ID and provider"""
        stmt = select(NotificationChannel).where(
            NotificationChannel.user_id == user_id,
            NotificationChannel.provider == provider
        )
        if active_only:
            stmt = stmt.where(NotificationChannel.is_active == True)
        return self.session.scalar(stmt)
    
    def update(self, channel_id: int, credentials: Optional[Dict[str, Any]] = None, 
               provider: Optional[str] = None, name: Optional[str] = None, 
               is_active: Optional[bool] = None, notification_hours: Optional[List[int]] = None) -> Optional[NotificationChannel]:
        """Update notification channel"""
        channel = self.get_by_id(channel_id)
        if not channel:
            return None
        
        if credentials is not None:
            channel.credentials = credentials
        if provider is not None:
            channel.provider = provider
        if name is not None:
            channel.name = name
        if notification_hours is not None:
            channel.notification_hours = notification_hours
        if is_active is not None:
            channel.is_active = is_active
            # If activating this channel, deactivate all other channels for this user
            if is_active:
                from sqlalchemy import update
                stmt = update(NotificationChannel).where(
                    NotificationChannel.user_id == channel.user_id,
                    NotificationChannel.id != channel_id,
                    NotificationChannel.is_active == True
                ).values(is_active=False)
                self.session.execute(stmt)
        
        self.session.flush()
        return channel
    
    def delete(self, channel_id: int) -> bool:
        """Delete notification channel by ID"""
        channel = self.get_by_id(channel_id)
        if not channel:
            return False
        
        self.session.delete(channel)
        self.session.flush()
        return True
    
    def deactivate(self, channel_id: int) -> Optional[NotificationChannel]:
        """Deactivate notification channel (soft delete)"""
        return self.update(channel_id, is_active=False)

