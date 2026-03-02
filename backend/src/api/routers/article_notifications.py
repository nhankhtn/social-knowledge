from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from ...api.dependencies import get_db, get_current_user
from ...database.models import (
    User,
    Article,
    ArticleNotification,
    NotificationChannel,
    Summary,
)
from ...schemas.article_notification import ArticleNotificationResponse


router = APIRouter(prefix="/article-notifications", tags=["article-notifications"])


@router.get("/me", response_model=List[ArticleNotificationResponse])
def get_my_article_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    channel_provider: Optional[str] = Query(
        None, description="Filter by notification channel provider"
    ),
    category_id: Optional[int] = Query(
        None, description="Filter by article category id"
    ),
    search: Optional[str] = Query(
        None, description="Search in article title or summary text"
    ),
):
    """
    List articles that have been sent to the current user via any notification channel.

    This is the data source for frontend 'Summaries' tab so users can read summaries on web.
    """
    # Base query: all notifications for this user, join article & channel for filtering
    query = (
        db.query(ArticleNotification)
        .join(Article, ArticleNotification.article_id == Article.id)
        .join(NotificationChannel, ArticleNotification.channel_id == NotificationChannel.id)
        .options(
            joinedload(ArticleNotification.article).joinedload(Article.category),
            joinedload(ArticleNotification.article).joinedload(Article.source),
            joinedload(ArticleNotification.channel),
        )
        .filter(ArticleNotification.user_id == current_user.id)
    )

    if channel_provider:
        query = query.filter(NotificationChannel.provider == channel_provider)

    if category_id:
        query = query.filter(Article.category_id == category_id)

    # Order by sent time (newest first)
    notifications = (
        query.order_by(ArticleNotification.sent_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Build response list with latest summary per article and optional search filter
    results: List[ArticleNotificationResponse] = []
    search_term = search.lower() if search else None

    for notification in notifications:
        article = notification.article

        # Get latest summary for this article
        summary = (
            db.query(Summary)
            .filter(Summary.article_id == article.id)
            .order_by(Summary.created_at.desc())
            .first()
        )

        if not summary:
            # Should not happen for sent notifications, but guard just in case
            continue

        if search_term:
            title = (article.title or "").lower()
            summary_text_lower = (summary.summary_text or "").lower()
            if search_term not in title and search_term not in summary_text_lower:
                continue

        results.append(
            ArticleNotificationResponse(
                id=notification.id,
                article_id=article.id,
                title=article.title,
                url=article.url,
                summary_text=summary.summary_text,
                sent_at=notification.sent_at,
                channel_provider=notification.channel.provider,
                category=article.category,
                source=article.source,
            )
        )

    return results

