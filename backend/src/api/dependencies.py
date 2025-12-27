from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Header
from ..database.connection import get_db_session
from ..database.models import User
from ..repositories import UserRepository
from ..utils.firebase_auth import verify_firebase_token


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session"""
    with get_db_session() as session:
        yield session


def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    # Verify Firebase token
    decoded_token = verify_firebase_token(token)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    firebase_uid = decoded_token.get("uid")
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing UID"
        )
    
    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get_by_firebase_uid(firebase_uid)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

