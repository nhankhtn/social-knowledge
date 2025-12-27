from pydantic import BaseModel
from datetime import datetime


class SummaryResponse(BaseModel):
    id: int
    article_id: int
    summary_text: str
    created_at: datetime
    
    class Config:
        from_attributes = True

