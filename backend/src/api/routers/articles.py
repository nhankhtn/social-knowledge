from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional

from ...schemas.article import ArticleResponse
from ...api.dependencies import get_db, get_admin_user
from ...database.models import User, Article

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=List[ArticleResponse])
def list_articles(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Search in title and content"),
):
    """List all articles (Admin only)"""
    query = db.query(Article).options(
        joinedload(Article.category),
        joinedload(Article.source)
    )
    
    if source_id:
        query = query.filter(Article.source_id == source_id)
    
    if category_id:
        query = query.filter(Article.category_id == category_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.content.ilike(search_term)
            )
        )
    
    articles = query.order_by(Article.crawled_at.desc()).offset(skip).limit(limit).all()
    
    return articles
