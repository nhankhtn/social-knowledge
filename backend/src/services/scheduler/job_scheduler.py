from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
import logging
import asyncio

from ...config.settings import settings
from ...database.connection import get_db_session
from ..crawler.service import CrawlerService
from ..ai.summarizer import Summarizer
from ..discord.bot import DiscordBot
from ..notifications.sender import NotificationSender
from ...database.models import Article, Summary, DiscordMessage, User, NotificationChannel, Category
from ...repositories import CategoryRepository

logger = logging.getLogger(__name__)


class JobScheduler:
    """Scheduler for automated news crawling and processing"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.timezone)
        self.discord_bot = DiscordBot()
        self.summarizer = Summarizer()
        self.notification_sender = NotificationSender()
    
    def _crawl_articles(self, db: Session) -> int:
        """Step 1: Crawl new articles from all sources"""
        logger.info("Step 1: Crawling articles from sources...")
        crawler = CrawlerService(db)
        total_crawled = crawler.crawl_all_sources()
        logger.info(f"Crawled {total_crawled} new articles")
        return total_crawled
    
    def _get_articles_to_process(self, db: Session, limit: int = 10) -> List[Article]:
        """Step 2: Get new articles without summaries (from last 24 hours)"""
        logger.info("Step 2: Getting articles to process...")
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        new_articles = db.query(Article).filter(
            ~Article.id.in_(
                db.query(Summary.article_id).distinct()
            ),
            Article.crawled_at >= one_day_ago
        ).limit(limit).all()
        
        logger.info(f"Found {len(new_articles)} articles to process")
        return new_articles
    
    def _get_categories_data(self, db: Session) -> Tuple[List[Category], List[Dict[str, str]]]:
        """Get all categories from database"""
        category_repo = CategoryRepository(db)
        all_categories = category_repo.get_all()
        categories_data = [
            {'id': cat.id, 'name': cat.name, 'slug': cat.slug}
            for cat in all_categories
        ]
        return all_categories, categories_data
    
    def _get_active_users(self, db: Session) -> List[User]:
        """Get all active users with notification channels and category preferences"""
        from sqlalchemy.orm import joinedload
        
        active_users = db.query(User).join(NotificationChannel).filter(
            NotificationChannel.is_active == True
        ).options(joinedload(User.category_preferences)).distinct().all()
        
        # Refresh each user to ensure category_preferences are loaded
        for user in active_users:
            db.refresh(user, ['category_preferences'])
        
        return active_users
    
    def _should_send_to_user(self, article: Article, user: User) -> bool:
        """Check if article should be sent to user based on their category preferences"""
        # If article has no category, send to all users
        if not article.category_id:
            return True
        
        # If user has no category preferences, send all articles
        if not user.category_preferences or len(user.category_preferences) == 0:
            return True
        
        # Check if article's category is in user's preferences
        user_category_ids = {cat.id for cat in user.category_preferences}
        return article.category_id in user_category_ids
    
    def _assign_category_to_article(self, article: Article, category_slug: Optional[str], all_categories: List[Category]) -> None:
        """Assign category to article if not already assigned"""
        if category_slug and not article.category_id:
            category = next(
                (cat for cat in all_categories if cat.slug == category_slug),
                None
            )
            if category:
                article.category_id = category.id
                logger.info(f"Assigned category '{category.name}' to article {article.id}")
    
    async def _process_batch_articles(self, db: Session, batch_articles: List[Article], 
                                all_categories: List[Category], categories_data: List[Dict[str, str]],
                                active_users: List[User]) -> int:
        """Process a batch of articles: summarize, classify, and send notifications"""
        if not batch_articles:
            return 0
        
        # Prepare articles data
        articles_data = [
            {
                'title': article.title,
                'content': article.content
            }
            for article in batch_articles
        ]
        
        # Summarize and classify in a single AI query
        logger.info(f"Summarizing and classifying {len(articles_data)} articles in batch...")
        results = self.summarizer.summarize_and_classify_batch(
            articles=articles_data,
            categories=categories_data,
            max_length=200
        )
        
        processed_count = 0
        
        for idx, article in enumerate(batch_articles):
            try:
                result = results[idx] if idx < len(results) else {'summary': '', 'category_slug': None}
                summary_text = result.get('summary', '')
                category_slug = result.get('category_slug')
                
                if not summary_text:
                    logger.warning(f"Empty summary for article {article.id}, skipping")
                    continue
                
                # Assign category
                self._assign_category_to_article(article, category_slug, all_categories)
                
                # Save summary
                summary = Summary(
                    article_id=article.id,
                    summary_text=summary_text
                )
                db.add(summary)
                db.flush()
                
                # Refresh article to load category relationship
                db.refresh(article, ['category'])
                
                # Send notifications to users who have this category in preferences
                for user in active_users:
                    # Check if user should receive this article
                    if not self._should_send_to_user(article, user):
                        continue
                    
                    for channel in user.notification_channels:
                        if not channel.is_active:
                            continue
                        
                        try:
                            category_name = article.category.name if article.category else None
                            await self.notification_sender.send(
                                provider=channel.provider,
                                credentials=channel.credentials,
                                title=article.title,
                                summary=summary_text,
                                url=article.url,
                                source_name=article.source.name,
                                category_name=category_name
                            )
                            logger.info(f"Sent to user {user.id} via {channel.provider} (category: {category_name or 'none'})")
                        except Exception as e:
                            logger.error(f"Failed to send to user {user.id} channel {channel.id}: {e}")
                
                logger.info(f"Processed article: {article.title[:50]}...")
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing article {article.id}: {e}")
                continue
        
        return processed_count
    
    async def _process_article_individual(self, db: Session, article: Article,
                                    all_categories: List[Category], categories_data: List[Dict[str, str]],
                                    active_users: List[User]) -> bool:
        """Process a single article individually (fallback method)"""
        try:
            # Summarize
            summary_text = self.summarizer.summarize_article(
                title=article.title,
                content=article.content,
                max_length=200
            )
            
            if not summary_text:
                logger.warning(f"Empty summary for article {article.id}, skipping")
                return False
            
            # Classify category
            if categories_data and not article.category_id:
                category_slug = self.summarizer.classify_category(
                    title=article.title,
                    content=article.content,
                    categories=categories_data
                )
                self._assign_category_to_article(article, category_slug, all_categories)
            
            # Save summary
            summary = Summary(
                article_id=article.id,
                summary_text=summary_text
            )
            db.add(summary)
            db.flush()
            
            # Refresh article to load category relationship
            db.refresh(article, ['category'])
            
            # Send notifications
            for user in active_users:
                # Check if user should receive this article
                if not self._should_send_to_user(article, user):
                    continue
                
                for channel in user.notification_channels:
                    if not channel.is_active:
                        continue
                    
                    try:
                        category_name = article.category.name if article.category else None
                        await self.notification_sender.send(
                            provider=channel.provider,
                            credentials=channel.credentials,
                            title=article.title,
                            summary=summary_text,
                            url=article.url,
                            source_name=article.source.name,
                            category_name=category_name
                        )
                        logger.info(f"Sent to user {user.id} via {channel.provider} (category: {category_name or 'none'})")
                    except Exception as e:
                        logger.error(f"Failed to send notification: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing article {article.id}: {e}")
            return False
    
    async def _process_articles(self, db: Session, new_articles: List[Article],
                         all_categories: List[Category], categories_data: List[Dict[str, str]],
                         active_users: List[User]) -> int:
        """Step 3: Process articles in batches"""
        logger.info("Step 3: Processing articles...")
        
        if not new_articles:
            return 0
        
        batch_size = settings.summary_batch_size
        total_processed = 0
        
        try:
            # Process articles in batches
            for batch_start in range(0, len(new_articles), batch_size):
                batch_end = min(batch_start + batch_size, len(new_articles))
                batch_articles = new_articles[batch_start:batch_end]
                
                logger.info(f"Processing batch {batch_start // batch_size + 1}: articles {batch_start + 1}-{batch_end} of {len(new_articles)}")
                
                try:
                    processed_count =await self._process_batch_articles(
                        db, batch_articles, all_categories, categories_data, active_users
                    )
                    
                    # Commit this batch
                    db.commit()
                    total_processed += processed_count
                    logger.info(f"Batch {batch_start // batch_size + 1} completed: {processed_count} articles processed")
                    
                except Exception as e:
                    logger.error(f"Error processing batch {batch_start // batch_size + 1}: {e}")
                    db.rollback()
                    
                    # Fallback to individual processing for this batch
                    logger.info(f"Falling back to individual processing for batch {batch_start // batch_size + 1}...")
                    for article in batch_articles:
                        if await self._process_article_individual(db, article, all_categories, categories_data, active_users):
                            db.commit()
                            total_processed += 1
                        else:
                            db.rollback()
            
            logger.info(f"Successfully processed {total_processed} out of {len(new_articles)} articles")
            return total_processed
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            db.rollback()
            
            # Fallback to individual processing
            logger.info("Falling back to individual article processing...")
            for article in new_articles:
                if await self._process_article_individual(db, article, all_categories, categories_data, active_users):
                    db.commit()
                    total_processed += 1
                else:
                    db.rollback()
            
            return total_processed
    
    async def crawl_and_process_job(self):
        """Main job: crawl, summarize, classify, and send notifications"""
        logger.info("Starting crawl and process job...")
        
        try:
            with get_db_session() as db:
                # Step 1: Crawl new articles
                self._crawl_articles(db)
                
                # Step 2: Get articles to process
                new_articles = self._get_articles_to_process(db, limit=10)
                
                if not new_articles:
                    logger.info("No articles to process")
                    return
                
                # Get categories and active users
                all_categories, categories_data = self._get_categories_data(db)
                active_users = self._get_active_users(db)
                
                # Step 3: Process articles
                total_processed = await self._process_articles(
                    db, new_articles, all_categories, categories_data, active_users
                )
                
                logger.info(f"Crawl and process job completed. Processed {total_processed} articles.")
                
        except Exception as e:
            logger.error(f"Error in crawl and process job: {e}")
    
    async def start(self):
        """Start the scheduler and Discord bot"""
        # Start Discord bot
        if self.discord_bot.token:
            asyncio.create_task(self.discord_bot.start())
            logger.info("Discord bot starting...")
        
        # Schedule job every 8 hours
        interval_hours = settings.crawl_interval_hours
        
        # Use interval trigger
        trigger = IntervalTrigger(hours=interval_hours)
        
        self.scheduler.add_job(
            self.crawl_and_process_job,
            trigger=trigger,
            id="crawl_and_process",
            name="Crawl and Process News",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started. Jobs will run every {interval_hours} hours.")
    
    async def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        await self.discord_bot.close()
        logger.info("Scheduler shutdown")
