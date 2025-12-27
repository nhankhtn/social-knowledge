from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone
import logging
import asyncio

from ...config.settings import settings
from ...database.connection import get_db_session
from ..crawler.service import CrawlerService
from ..ai.summarizer import Summarizer
from ..discord.bot import DiscordBot
from ..notifications.sender import NotificationSender
from ...database.models import Article, Summary, DiscordMessage, User, NotificationChannel

logger = logging.getLogger(__name__)


class JobScheduler:
    """Scheduler for automated news crawling and processing"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.timezone)
        self.discord_bot = DiscordBot()
        self.summarizer = Summarizer()
        self.notification_sender = NotificationSender()
    
    async def crawl_and_process_job(self):
        """Main job: crawl, summarize, and send to Discord"""
        logger.info("Starting crawl and process job...")
        
        try:
            with get_db_session() as db:
                # Step 1: Crawl new articles
                crawler = CrawlerService(db)
                total_crawled = crawler.crawl_all_sources()
                logger.info(f"Crawled {total_crawled} new articles")
                
                # Step 2: Get new articles without summaries (from last 24 hours)
                one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
                new_articles = db.query(Article).filter(
                    ~Article.id.in_(
                        db.query(Summary.article_id).distinct()
                    ),
                    Article.crawled_at >= one_day_ago
                ).limit(10).all()  # Process max 10 at a time
                
                logger.info(f"Found {len(new_articles)} articles to summarize")
                
                # Step 3: Summarize and send notifications
                for article in new_articles:
                    try:
                        # Generate summary
                        summary_text = self.summarizer.summarize_article(
                            title=article.title,
                            content=article.content,
                            max_length=200
                        )
                        
                        # Save summary
                        summary = Summary(
                            article_id=article.id,
                            summary_text=summary_text
                        )
                        db.add(summary)
                        db.flush()
                        
                        # Send to Discord bot (legacy support)
                        # if self.discord_bot.token and settings.discord_channel_id:
                        #     message_id = await self.discord_bot.send_summary(
                        #         title=article.title,
                        #         summary=summary_text,
                        #         url=article.url,
                        #         source_name=article.source.name
                        #     )
                            
                        #     if message_id:
                        #         discord_msg = DiscordMessage(
                        #             summary_id=summary.id,
                        #             channel_id=settings.discord_channel_id,
                        #             message_id=message_id
                        #         )
                        #         db.add(discord_msg)
                        
                        # Send to all active user notification channels
                        active_users = db.query(User).join(NotificationChannel).filter(
                            NotificationChannel.is_active == True
                        ).distinct().all()
                        
                        for user in active_users:
                            for channel in user.notification_channels:
                                if not channel.is_active:
                                    continue
                                
                                try:
                                    await self.notification_sender.send(
                                        provider=channel.provider,
                                        credentials=channel.credentials,
                                        title=article.title,
                                        summary=summary_text,
                                        url=article.url,
                                        source_name=article.source.name
                                    )
                                    logger.info(f"Sent to user {user.id} via {channel.provider}")
                                except Exception as e:
                                    logger.error(f"Failed to send to user {user.id} channel {channel.id}: {e}")
                        
                        db.commit()
                        logger.info(f"Processed article: {article.title[:50]}...")
                        
                    except Exception as e:
                        logger.error(f"Error processing article {article.id}: {e}")
                        db.rollback()
                        continue
                
                logger.info("Crawl and process job completed")
                
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
        trigger = IntervalTrigger(hours=16, minutes=44)
        
        self.scheduler.add_job(
            self.crawl_and_process_job,
            trigger=trigger,
            id="crawl_and_process",
            name="Crawl and Process News",
            replace_existing=True
        )

        await self.crawl_and_process_job()
        
        self.scheduler.start()
        logger.info(f"Scheduler started. Jobs will run every {interval_hours} hours.")
    
    async def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        await self.discord_bot.close()
        logger.info("Scheduler shutdown")

