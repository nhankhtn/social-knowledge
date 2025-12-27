import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import logging

from .base_crawler import BaseCrawler, ArticleData

logger = logging.getLogger(__name__)


class RSSParser(BaseCrawler):
    """RSS feed parser and crawler"""
    
    def __init__(self, source_url: str):
        super().__init__(source_url)
        self.timeout = 30
    
    def crawl(self) -> List[ArticleData]:
        """Parse RSS feed and extract articles"""
        articles = []
        
        try:
            feed = feedparser.parse(self.source_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"RSS parsing error: {feed.bozo_exception}")
                return articles
            
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing entry: {e}")
                    continue
            
            logger.info(f"Crawled {len(articles)} articles from {self.source_url}")
            
        except Exception as e:
            logger.error(f"Error crawling RSS feed {self.source_url}: {e}")
        
        return articles
    
    def _parse_entry(self, entry) -> Optional[ArticleData]:
        """Parse a single RSS entry"""
        url = entry.get("link", "").strip()
        if not url:
            return None
        
        title = self.clean_text(entry.get("title", ""))
        if not title:
            return None
        
        # Try to get content from different fields
        content = ""
        if "content" in entry and len(entry.content) > 0:
            content = entry.content[0].get("value", "")
        elif "summary" in entry:
            content = entry.summary
        elif "description" in entry:
            content = entry.description
        
        # Clean HTML from content
        content = self._clean_html(content)
        content = self.clean_text(content)
        
        # Parse published date
        published_date = None
        if "published_parsed" in entry and entry.published_parsed:
            try:
                published_date = datetime(*entry.published_parsed[:6])
            except Exception:
                pass
        
        # If content is too short, try to fetch full article
        if len(content) < 200:
            full_content = self._fetch_full_article(url)
            if full_content:
                content = full_content
        
        return ArticleData(
            url=url,
            title=title,
            content=content,
            published_date=published_date
        )
    
    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from content"""
        if not html:
            return ""
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        return text
    
    def _fetch_full_article(self, url: str) -> Optional[str]:
        """Fetch full article content from URL"""
        try:
            response = requests.get(url, timeout=self.timeout, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find main content
            content_selectors = [
                "article",
                ".article-content",
                ".post-content",
                ".entry-content",
                "main",
                "#main-content",
                ".content"
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                content = soup.find("body")
            
            if content:
                text = content.get_text()
                return self.clean_text(text)
            
        except Exception as e:
            logger.debug(f"Could not fetch full article from {url}: {e}")
        
        return None

