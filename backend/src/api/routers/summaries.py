from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from ...api.dependencies import get_db, get_current_user
from ...database.models import User, Article, Summary
from ...schemas.summarized_article import SummarizedArticleResponse


router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.get("", response_model=List[SummarizedArticleResponse])
def list_summarized_articles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category_id: Optional[int] = Query(
        None, description="Filter by article category id"
    ),
    source_id: Optional[int] = Query(
        None, description="Filter by article source id"
    ),
    search: Optional[str] = Query(
        None, description="Search in article title or summary text"
    ),
):
    """
    Return list of articles that already have summaries.

    This is used by frontend to show 'all summaries' with filters.
    """
    query = (
        db.query(Summary, Article)
        .join(Article, Summary.article_id == Article.id)
        .options(
            joinedload(Article.category),
            joinedload(Article.source),
        )
    )

    if category_id is not None:
        query = query.filter(Article.category_id == category_id)

    if source_id is not None:
        query = query.filter(Article.source_id == source_id)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(like),
                Summary.summary_text.ilike(like),
            )
        )

    # Order by latest summarized first
    rows = (
        query.order_by(Summary.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    results: List[SummarizedArticleResponse] = []

    for summary, article in rows:
        results.append(
            SummarizedArticleResponse(
                article_id=article.id,
                title=article.title,
                url=article.url,
                summary_text=summary.summary_text,
                summarized_at=summary.created_at,
                category=article.category,
                source=article.source,
            )
        )

    return results

