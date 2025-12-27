"""
Crawler for Báo Thanh Niên (thanhnien.vn)
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import logging
import re
from urllib.parse import urlparse

from ..base_crawler import BaseCrawler, ArticleData

logger = logging.getLogger(__name__)


class ThanhNienCrawler(BaseCrawler):
    """Crawler for Báo Thanh Niên"""
    
    def __init__(self, source_url: str):
        super().__init__(source_url)
        self.timeout = 30
        # Extract base URL from source_url
        parsed = urlparse(source_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def crawl(self) -> List[ArticleData]:
        """Crawl articles from Thanh Niên homepage"""
        articles = []
        
        try:
            response = requests.get(self.source_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find all article links
            article_links = self._extract_article_links(soup)
            
            logger.info(f"Found {len(article_links)} article links on homepage")
            
            # Crawl each article
            for link in article_links[:20]:  # Limit to 20 articles per crawl
                try:
                    article = self._crawl_article(link)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Error crawling article {link}: {e}")
                    continue
            
            logger.info(f"Crawled {len(articles)} articles from Thanh Niên")
            
        except Exception as e:
            logger.error(f"Error crawling Thanh Niên {self.source_url}: {e}")
        
        return articles
    
    def _extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from homepage"""
        links = set()
        
        # Find links with class "box-category-link-title" (main article links)
        for link in soup.find_all("a", class_="box-category-link-title"):
            href = link.get("href", "")
            if href and href.endswith(".htm"):
                # Convert relative URLs to absolute
                if href.startswith("/"):
                    full_url = f"{self.base_url}{href}"
                else:
                    full_url = href
                links.add(full_url)
        
        # Also find links in h3.box-title-text > a
        for h3 in soup.find_all("h3", class_="box-title-text"):
            link = h3.find("a")
            if link:
                href = link.get("href", "")
                if href and href.endswith(".htm"):
                    if href.startswith("/"):
                        full_url = f"{self.base_url}{href}"
                    else:
                        full_url = href
                    links.add(full_url)
        
        return list(links)
    
    def _crawl_article(self, url: str) -> Optional[ArticleData]:
        """Crawl a single article page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract title
            title = self._extract_title(soup)
            if not title:
                logger.warning(f"Could not extract title from {url}")
                return None
            
            # Extract content
            content = self._extract_content(soup)
            if not content or len(content) < 100:
                logger.warning(f"Content too short or empty from {url}")
                return None
            
            # Extract published date
            published_date = self._extract_published_date(soup, url)
            
            return ArticleData(
                url=url,
                title=title,
                content=content,
                published_date=published_date
            )
            
        except Exception as e:
            logger.error(f"Error crawling article {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title"""
        # Try multiple selectors
        selectors = [
            "h1.detail-title",
            "h1.detail__title",
            "h1.article-title",
            "h1",
            ".detail-title",
            "meta[property='og:title']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith("meta"):
                    title = element.get("content", "").strip()
                else:
                    title = element.get_text().strip()
                
                if title:
                    return self.clean_text(title)
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try multiple content selectors
        content_selectors = [
            ".detail-content",
            ".detail__content",
            ".article-content",
            ".article-body",
            ".detail-body",
            "[class*='detail-content']",
            "[class*='article-content']",
            "article",
            "main"
        ]
        
        content = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Get all paragraphs
                paragraphs = content_elem.find_all("p")
                if paragraphs:
                    texts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                    if texts:
                        content = "\n\n".join(texts)
                        break
        
        if not content:
            # Fallback: try to find main content area
            main = soup.find("main") or soup.find("article")
            if main:
                paragraphs = main.find_all("p")
                texts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                if texts:
                    content = "\n\n".join(texts)
        
        if content:
            return self.clean_text(content)
        
        return None
    
    def _extract_published_date(self, soup: BeautifulSoup, url: str) -> Optional[datetime]:
        """Extract published date from article"""
        # Try meta tags first
        meta_date = soup.find("meta", property="article:published_time")
        if meta_date:
            date_str = meta_date.get("content", "")
            if date_str:
                try:
                    from dateutil import parser
                    return parser.parse(date_str)
                except:
                    try:
                        # Fallback to datetime.strptime for ISO format
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except:
                        pass
        
        # Try time tag
        time_tag = soup.find("time")
        if time_tag:
            datetime_attr = time_tag.get("datetime")
            if datetime_attr:
                try:
                    from dateutil import parser
                    return parser.parse(datetime_attr)
                except:
                    try:
                        return datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))
                    except:
                        pass
        
        return None

