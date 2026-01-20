from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None


class UserLogin(BaseModel):
    firebase_token: str
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    photo_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    firebase_uid: str
    role: str = "USER"
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

