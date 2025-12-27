from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleData:
    """Data structure for crawled article"""
    url: str
    title: str
    content: str
    published_date: Optional[datetime] = None


class BaseCrawler(ABC):
    """Base class for news crawlers"""
    
    def __init__(self, source_url: str):
        self.source_url = source_url
    
    @abstractmethod
    def crawl(self) -> List[ArticleData]:
        """
        Crawl articles from the source
        
        Returns:
            List of ArticleData objects
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove extra whitespace
        text = " ".join(text.split())
        return text.strip()

