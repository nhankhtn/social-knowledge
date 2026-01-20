from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Header, Request
from ..database.connection import get_db_session
from ..database.models import User
from ..repositories import UserRepository
from ..utils.firebase_auth import verify_firebase_token
from typing import Optional


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session"""
    with get_db_session() as session:
        yield session


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Authorization header"""
    # Check if already verified by middleware (reuse cached result)
    if hasattr(request.state, "decoded_token") and hasattr(request.state, "firebase_uid"):
        firebase_uid = request.state.firebase_uid
        decoded_token = request.state.decoded_token
    else:
        # Verify token if not already done by middleware
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
        
        # Cache for potential reuse
        request.state.firebase_uid = firebase_uid
        request.state.decoded_token = decoded_token
    
    # Get user from database (only query DB once)
    user_repo = UserRepository(db)
    user = user_repo.get_by_firebase_uid(firebase_uid)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Set user_id in request state for rate limiting and other uses
    request.state.user_id = user.id
    
    return user


def get_admin_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user and verify they are ADMIN"""
    user = get_current_user(request, authorization, db)
    
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    return user

