from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ...repositories import UserRepository
from ...database.models import User
from ...schemas.user import UserLogin, UserResponse, UserUpdate
from ...api.dependencies import get_db, get_current_user
from ...utils.firebase_auth import verify_firebase_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=UserResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login/Register user with Firebase token
    Verifies Firebase token and creates or updates user
    """
    # Verify Firebase token
    decoded_token = verify_firebase_token(user_data.firebase_token)
    
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )
    
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email") or user_data.email
    
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: missing UID"
        )
    
    repo = UserRepository(db)
    
    # Check if user exists
    user = repo.get_by_firebase_uid(firebase_uid)

    print("Authenticated user:", user_data.email, "UID:", firebase_uid)
    
    if user:
        # Update last login and user info
        repo.update(
            user.id,
            display_name=user_data.display_name or user.display_name,
            photo_url=user_data.photo_url or user.photo_url,
            last_login_at=datetime.now(timezone.utc)
        )
        db.commit()
        db.refresh(user)
    else:
        # Create new user
        user = repo.create(
            firebase_uid=firebase_uid,
            email=email,
            display_name=user_data.display_name,
            photo_url=user_data.photo_url
        )
        db.commit()
        db.refresh(user)
    
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user"""
    
    repo = UserRepository(db)
    updated_user = repo.update(
        current_user.id,
        display_name=user_update.display_name,
        photo_url=user_update.photo_url
    )
    
    db.commit()
    db.refresh(updated_user)
    
    return updated_user




