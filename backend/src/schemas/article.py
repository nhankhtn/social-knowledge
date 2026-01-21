from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryInfo(BaseModel):
    """Category information for article response"""
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True


class SourceInfo(BaseModel):
    """Source information for article response"""
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True


class ArticleResponse(BaseModel):
    id: int
    url: str
    title: str
    content: str
    published_date: Optional[datetime]
    crawled_at: datetime
    source_id: int
    category_id: Optional[int] = None
    category: Optional[CategoryInfo] = None
    source: Optional[SourceInfo] = None
    
    class Config:
        from_attributes = True

