from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ArticleResponse(BaseModel):
    id: int
    url: str
    title: str
    content: str
    published_date: Optional[datetime]
    crawled_at: datetime
    source_id: int
    category_id: Optional[int] = None
    
    class Config:
        from_attributes = True

