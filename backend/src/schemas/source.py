from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SourceBase(BaseModel):
    name: str
    url: str


class SourceCreate(SourceBase):
    slug: str


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    url: Optional[str] = None


class SourceResponse(SourceBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

