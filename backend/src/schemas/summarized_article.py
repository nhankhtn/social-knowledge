from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .article import CategoryInfo, SourceInfo


class SummarizedArticleResponse(BaseModel):
    """Article that already has at least one summary, flattened view for listing."""

    article_id: int
    title: str
    url: str
    summary_text: str
    summarized_at: datetime
    category: Optional[CategoryInfo] = None
    source: Optional[SourceInfo] = None

