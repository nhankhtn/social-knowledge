"""
Crawler for BBC News (bbc.com/news)
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import logging
import re
from urllib.parse import urlparse, urljoin

from ..base_crawler import BaseCrawler, ArticleData
from ....config.settings import settings

logger = logging.getLogger(__name__)


class BBCCrawler(BaseCrawler):
    """Crawler for BBC News"""
    
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
        """Crawl articles from BBC News homepage"""
        articles = []
        
        try:
            response = requests.get(self.source_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find all article links
            article_links = self._extract_article_links(soup)
            
            logger.info(f"Found {len(article_links)} article links on homepage")
            
            # Crawl each article
            limit = settings.crawl_articles_limit
            for link in article_links[:limit]:
                try:
                    article = self._crawl_article(link)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Error crawling article {link}: {e}")
                    continue
            
            logger.info(f"Crawled {len(articles)} articles from BBC News")
            
        except Exception as e:
            logger.error(f"Error crawling BBC News {self.source_url}: {e}")
        
        return articles
    
    def _extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from homepage"""
        links = set()
        
        # BBC News article URLs typically have format: bbc.com/news/... or bbc.co.uk/news/...
        # Find all links that look like article URLs
        selectors = [
            "a[href*='/news/']",
            "a[href*='bbc.com/news']",
            "a[href*='bbc.co.uk/news']",
            "[data-testid='topic-promos'] a",
            "[data-testid='topic-list'] a",
            "article a",
            "h2 a",
            "h3 a",
            "[class*='promo'] a",
            "[class*='story'] a",
        ]
        
        for selector in selectors:
            for link in soup.select(selector):
                href = link.get("href", "")
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith("/"):
                        full_url = urljoin(self.base_url, href)
                    elif href.startswith("http"):
                        full_url = href
                    else:
                        full_url = urljoin(self.base_url, "/" + href)
                    
                    # Filter to only BBC News article URLs
                    if self._is_article_url(full_url):
                        links.add(full_url)
        
        return list(links)
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is an article URL"""
        # Must be from bbc.com or bbc.co.uk domain
        if "bbc.com" not in url and "bbc.co.uk" not in url:
            return False
        
        # Must be a news article (contains /news/)
        if "/news/" not in url:
            return False
        
        # Exclude common non-article pages
        excluded_patterns = [
            "/rss",
            "/sitemap",
            "/search",
            "/tag",
            "/author",
            "/category",
            "/live",
            "/av/",
            "/sport",
            "/weather",
            "/travel",
            "/culture",
            "/future",
            "/worklife",
            "/reel",
            "/newsround",
            "/newsbeat",
            "/topics/",
            "/correspondents/",
            "/programmes/",
            "/help",
            "/terms",
            "/privacy",
            "/about",
            "/contact",
            "/news/help",
            "/news/terms",
            "/news/privacy",
        ]
        
        for pattern in excluded_patterns:
            if pattern in url.lower():
                return False
        
        # BBC News article URLs typically:
        # - Have format: bbc.com/news/...-12345678 or bbc.com/news/world-...-12345678
        # - Contain article ID (numbers) at the end
        # - Or have date pattern: /news/.../2025/01/20/...
        
        # Check if URL has article ID pattern (numbers at the end)
        match = re.search(r'-(\d{8,})/?$', url)
        if match:
            return True
        
        # Check for date pattern: /news/.../2025/01/20/...
        if re.search(r'/news/.*/\d{4}/\d{2}/\d{2}/', url):
            return True
        
        # Accept URLs with reasonable article path structure
        # Should have at least 2 segments after /news/
        path = urlparse(url).path
        if path.startswith("/news/"):
            segments = [s for s in path.split("/") if s]
            if len(segments) >= 2:  # /news/category/article-name
                # Exclude very short segments (likely not articles)
                if len(segments[-1]) > 5:
                    return True
        
        return False
    
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
        # Try multiple selectors based on BBC structure
        selectors = [
            "h1[data-testid='headline']",
            "h1[id='main-heading']",
            "h1.article-headline",
            "h1[class*='headline']",
            "h1",
            "meta[property='og:title']",
            "meta[name='title']",
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith("meta"):
                    title = element.get("content", "").strip()
                else:
                    title = element.get_text().strip()
                
                if title:
                    # Remove site name suffix if present
                    title = re.sub(r'\s*\|\s*BBC\s+News.*$', '', title, flags=re.IGNORECASE)
                    title = re.sub(r'\s*-\s*BBC\s+News.*$', '', title, flags=re.IGNORECASE)
                    return self.clean_text(title)
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside", "figure", "iframe"]):
            script.decompose()
        
        # Try multiple content selectors based on BBC structure
        content_selectors = [
            "[data-testid='article-body']",
            "[data-component='text-block']",
            "article[data-testid='article']",
            "[class*='article-body']",
            "[class*='story-body']",
            "[class*='article-content']",
            "[itemprop='articleBody']",
            "article",
            "main",
        ]
        
        content = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Get all paragraphs
                paragraphs = content_elem.find_all("p")
                if paragraphs:
                    texts = []
                    for p in paragraphs:
                        text = p.get_text().strip()
                        # Skip empty paragraphs and common non-content elements
                        if text and len(text) > 10:
                            # Skip common footer/header text
                            if not any(skip in text.lower() for skip in [
                                "read more", "related", "related stories",
                                "comment", "share", "subscribe", "follow",
                                "video", "image", "photograph", "getty images",
                                "external links", "related topics", "more on this story"
                            ]):
                                texts.append(text)
                    
                    if texts:
                        content = "\n\n".join(texts)
                        break
        
        if not content:
            # Fallback: try to find main content area
            main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile("content|body|story"))
            if main:
                paragraphs = main.find_all("p")
                texts = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 10:
                        if not any(skip in text.lower() for skip in [
                            "read more", "related", "comment", "share"
                        ]):
                            texts.append(text)
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
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except:
                        pass
        
        # Try other meta tags
        meta_date = soup.find("time", {"data-testid": "timestamp"})
        if meta_date:
            datetime_attr = meta_date.get("datetime")
            if datetime_attr:
                try:
                    from dateutil import parser
                    return parser.parse(datetime_attr)
                except:
                    try:
                        return datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))
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
        
        # Try to find date in article metadata
        date_elem = soup.find("div", {"data-testid": "timestamp"}) or soup.find("time")
        if date_elem:
            datetime_attr = date_elem.get("datetime")
            if datetime_attr:
                try:
                    from dateutil import parser
                    return parser.parse(datetime_attr)
                except:
                    pass
            else:
                date_text = date_elem.get_text().strip()
                if date_text:
                    try:
                        from dateutil import parser
                        return parser.parse(date_text)
                    except:
                        pass
        
        # Try to extract from URL if it contains date pattern
        # Pattern: .../2025/01/20/... or ...-20250120-...
        match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if match:
            try:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day))
            except:
                pass
        
        # Try article ID pattern: ...-20250120...
        match = re.search(r'-(\d{8})', url)
        if match:
            date_str = match.group(1)
            try:
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                return datetime(year, month, day)
            except:
                pass
        
        return None
