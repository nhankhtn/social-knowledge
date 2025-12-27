from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database.models import User


class UserRepository:
    """Repository for User operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, firebase_uid: str, email: str, display_name: Optional[str] = None, photo_url: Optional[str] = None) -> User:
        """Create a new user"""
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            photo_url=photo_url
        )
        self.session.add(user)
        self.session.flush()
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.get(User, user_id)
    
    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        return self.session.scalar(stmt)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        return self.session.scalar(stmt)
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        self.session.flush()
        return user
    

