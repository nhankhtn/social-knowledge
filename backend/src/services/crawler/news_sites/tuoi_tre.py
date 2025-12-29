"""
Crawler for Báo Tuổi Trẻ (tuoitre.vn)
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import logging
import re
from urllib.parse import urlparse, urljoin

from ..base_crawler import BaseCrawler, ArticleData

logger = logging.getLogger(__name__)


class TuoiTreCrawler(BaseCrawler):
    """Crawler for Báo Tuổi Trẻ"""
    
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
        """Crawl articles from Tuổi Trẻ homepage"""
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
            
            logger.info(f"Crawled {len(articles)} articles from Tuổi Trẻ")
            
        except Exception as e:
            logger.error(f"Error crawling Tuổi Trẻ {self.source_url}: {e}")
        
        return articles
    
    def _extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from homepage"""
        links = set()
        
        # Find links in article cards/list items
        # Tuổi Trẻ uses various selectors for article links
        selectors = [
            "a[href*='.htm']",  # All links ending with .htm
            ".box-category-link-title a",
            ".article-title a",
            "h3 a",
            "h2 a",
            ".title-news a",
            ".box-title-text a",
        ]
        
        for selector in selectors:
            for link in soup.select(selector):
                href = link.get("href", "")
                if href and ".htm" in href:
                    # Convert relative URLs to absolute
                    if href.startswith("/"):
                        full_url = urljoin(self.base_url, href)
                    elif href.startswith("http"):
                        full_url = href
                    else:
                        full_url = urljoin(self.base_url, "/" + href)
                    
                    # Filter out non-article URLs
                    if self._is_article_url(full_url):
                        links.add(full_url)
        
        return list(links)
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is an article URL"""
        # Tuổi Trẻ article URLs typically have format: tuoitre.vn/...-YYYYMMDDHHMMSSSSS.htm
        if not url.endswith(".htm"):
            return False
        
        # Exclude common non-article pages
        excluded_patterns = [
            "/rss",
            "/sitemap",
            "/search",
            "/tag",
            "/author",
            "/category",
            "/chuyen-muc",
            "/danh-muc",
            "/tim-kiem",
            "/lien-he",
            "/gioi-thieu",
            "/quy-dinh",
            "/chinh-sach",
        ]
        
        for pattern in excluded_patterns:
            if pattern in url.lower():
                return False
        
        # Check if URL has article ID pattern (numbers at the end before .htm)
        # Pattern: ...-20251229222801915.htm
        match = re.search(r'-(\d{15,})\.htm$', url)
        if match:
            return True
        
        # Also accept URLs with date-like patterns
        if re.search(r'/\d{4}/\d{2}/\d{2}/', url):
            return True
        
        return True  # Default to True if passes other checks
    
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
        # Try multiple selectors based on Tuổi Trẻ structure
        selectors = [
            "h1.detail-title.article-title",
            "h1.detail-title",
            "h1.article-title",
            "h1[data-role='title']",
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
                    return self.clean_text(title)
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside", "figure"]):
            script.decompose()
        
        # Try multiple content selectors based on Tuổi Trẻ structure
        content_selectors = [
            ".detail-content.afcbc-body",
            ".detail-content",
            "[data-role='content']",
            ".article-content",
            ".article-body",
            ".detail-body",
            "[class*='detail-content']",
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
                                "đọc thêm", "xem thêm", "liên quan", "tin liên quan",
                                "bình luận", "chia sẻ", "đăng ký", "theo dõi"
                            ]):
                                texts.append(text)
                    
                    if texts:
                        content = "\n\n".join(texts)
                        break
        
        if not content:
            # Fallback: try to find main content area
            main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile("content|body|detail"))
            if main:
                paragraphs = main.find_all("p")
                texts = [p.get_text().strip() for p in paragraphs if p.get_text().strip() and len(p.get_text().strip()) > 10]
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
        
        # Try data-role="publishdate"
        publish_date_elem = soup.find("div", {"data-role": "publishdate"})
        if publish_date_elem:
            date_text = publish_date_elem.get_text().strip()
            if date_text:
                try:
                    # Format: "29/12/2025 22:32 GMT+7"
                    from dateutil import parser
                    # Remove GMT+7 and parse
                    date_text_clean = re.sub(r'\s*GMT[+-]\d+', '', date_text)
                    return parser.parse(date_text_clean, dayfirst=True)
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
        
        # Try to extract from URL if it contains date pattern
        # Pattern: ...-20251229222801915.htm
        match = re.search(r'-(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})', url)
        if match:
            try:
                year, month, day, hour, minute = match.groups()
                return datetime(int(year), int(month), int(day), int(hour), int(minute))
            except:
                pass
        
        return None
