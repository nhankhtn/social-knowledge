from typing import List
from sqlalchemy.orm import Session
import logging

from ...database.models import Source, Article
from ...repositories import SourceRepository
from .rss_parser import RSSParser
from .news_sites import ThanhNienCrawler, TuoiTreCrawler

logger = logging.getLogger(__name__)


class CrawlerService:
    """Service for crawling news from sources"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = SourceRepository(db)
    
    def crawl_all_sources(self) -> int:
        """Crawl all active sources"""
        sources = self.repo.get_all()
        total_articles = 0
        
        for source in sources:
            try:
                articles = self.crawl_source(source)
                total_articles += len(articles)
            except Exception as e:
                logger.error(f"Error crawling source {source.id} ({source.name}): {e}")
                continue
        
        return total_articles
    
    def _get_crawler(self, source: Source):
        """Get appropriate crawler based on source slug"""
        slug = source.slug.lower()
        
        if slug == "bao-thanh-nien":
            return ThanhNienCrawler(source.url)
        elif slug == "bao-tuoi-tre" or slug == "tuoi-tre" or "tuoitre" in slug:
            return TuoiTreCrawler(source.url)
        else:
            # Default to RSS parser
            return RSSParser(source.url)
    
    def crawl_source(self, source: Source) -> List[Article]:
        """Crawl articles from a specific source"""
        logger.info(f"Crawling source: {source.name} ({source.slug}) - {source.url}")
        
        # Get appropriate crawler based on source slug
        crawler = self._get_crawler(source)
        articles_data = crawler.crawl()
        
        saved_articles = []
        
        for article_data in articles_data:
            # Check if article already exists
            existing = self.db.query(Article).filter(Article.url == article_data.url).first()
            if existing:
                continue
            
            # Create new article (category will be assigned by AI later)
            article = Article(
                url=article_data.url,
                title=article_data.title,
                content=article_data.content,
                published_date=article_data.published_date,
                source_id=source.id,
                category_id=None  # Will be assigned by AI during summarization
            )
            
            self.db.add(article)
            saved_articles.append(article)
        
        self.db.commit()
        
        logger.info(f"Saved {len(saved_articles)} new articles from {source.name}")
        return saved_articles

