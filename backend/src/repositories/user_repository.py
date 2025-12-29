from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database.models import User, Category


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
    
    def set_category_preferences(self, user_id: int, category_ids: List[int]) -> Optional[User]:
        """Set user category preferences (replaces existing)"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        # Get categories by IDs
        categories = self.session.query(Category).filter(Category.id.in_(category_ids)).all()
        
        # Replace existing preferences
        user.category_preferences = categories
        self.session.flush()
        return user
    
    def add_category_preference(self, user_id: int, category_id: int) -> Optional[User]:
        """Add a category to user preferences"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        category = self.session.get(Category, category_id)
        if not category:
            return None
        
        if category not in user.category_preferences:
            user.category_preferences.append(category)
            self.session.flush()
        
        return user
    
    def remove_category_preference(self, user_id: int, category_id: int) -> Optional[User]:
        """Remove a category from user preferences"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        category = self.session.get(Category, category_id)
        if category and category in user.category_preferences:
            user.category_preferences.remove(category)
            self.session.flush()
        
        return user


