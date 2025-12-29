from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ...repositories import NotificationRepository
from ...database.models import User
from ...schemas.notification import NotificationChannelCreate, NotificationChannelUpdate, NotificationChannelResponse
from ...api.dependencies import get_db, get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("", response_model=NotificationChannelResponse, status_code=status.HTTP_201_CREATED)
def create_notification_channel(
    channel: NotificationChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification channel for user"""
    notification_repo = NotificationRepository(db)
    
    # Check if channel with same provider already exists for this user
    existing = notification_repo.get_by_user_and_provider(current_user.id, channel.provider)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Notification channel with provider '{channel.provider}' already exists for this user"
        )
    
    new_channel = notification_repo.create(
        user_id=current_user.id,
        provider=channel.provider,
        credentials=channel.credentials,
        name=channel.name
    )
    
    db.commit()
    db.refresh(new_channel)
    
    return new_channel


@router.get("", response_model=List[NotificationChannelResponse])
def list_notification_channels(
    current_user: User = Depends(get_current_user),
    active_only: bool = Query(True, description="Only return active channels"),
    db: Session = Depends(get_db)
):
    """Get all notification channels for user"""
    notification_repo = NotificationRepository(db)
    channels = notification_repo.get_by_user_id(current_user.id, active_only=active_only)
    
    return channels


@router.get("/{channel_id}", response_model=NotificationChannelResponse)
def get_notification_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification channel by ID"""
    notification_repo = NotificationRepository(db)
    channel = notification_repo.get_by_id(channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification channel not found"
        )
    
    if channel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this notification channel"
        )
    
    return channel


@router.put("/{channel_id}", response_model=NotificationChannelResponse)
def update_notification_channel(
    channel_id: int,
    channel_update: NotificationChannelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification channel"""
    notification_repo = NotificationRepository(db)
    channel = notification_repo.get_by_id(channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification channel not found"
        )
    
    if channel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this notification channel"
        )
    
    # Check if new provider conflicts with existing channel
    if channel_update.provider and channel_update.provider != channel.provider:
        existing = notification_repo.get_by_user_and_provider(current_user.id, channel_update.provider)
        if existing and existing.id != channel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification channel with provider '{channel_update.provider}' already exists"
            )
    
    updated_channel = notification_repo.update(
        channel_id,
        credentials=channel_update.credentials,
        provider=channel_update.provider,
        name=channel_update.name,
        is_active=channel_update.is_active
    )
    
    db.commit()
    db.refresh(updated_channel)
    
    return updated_channel


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete notification channel (soft delete - deactivates it)"""
    notification_repo = NotificationRepository(db)
    channel = notification_repo.get_by_id(channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification channel not found"
        )
    
    if channel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this notification channel"
        )
    
    notification_repo.deactivate(channel_id)
    db.commit()
    
    return None

