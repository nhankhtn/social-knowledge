from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .article import CategoryInfo, SourceInfo


class ArticleNotificationResponse(BaseModel):
    """Article notification item for current user (what has been sent to them)."""

    id: int
    article_id: int
    title: str
    url: str
    summary_text: str
    sent_at: datetime
    channel_provider: str
    category: Optional[CategoryInfo] = None
    source: Optional[SourceInfo] = None

    class Config:
        from_attributes = True

