from typing import Optional, List, Dict
from .providers.gemini_provider import GeminiProvider


class Summarizer:
    """AI Summarization service"""
    
    def __init__(self, provider: Optional[GeminiProvider] = None):
        self.provider = provider or GeminiProvider()
    
    def summarize_article(self, title: str, content: str, max_length: int = 200) -> str:
        """
        Summarize an article
        
        Args:
            title: Article title
            content: Article content
            max_length: Maximum length of summary
            
        Returns:
            Summary text
        """
        full_text = f"{title}\n\n{content}"
        return self.provider.summarize(full_text, max_length=max_length)
    
    def summarize_articles_batch(self, articles: List[Dict[str, str]], max_length: int = 200) -> List[str]:
        """
        Summarize multiple articles in batch
        
        Args:
            articles: List of dicts with 'title' and 'content' keys
            max_length: Maximum length of each summary
            
        Returns:
            List of summary texts in the same order as input articles
        """
        return self.provider.summarize_batch(articles, max_length=max_length)
    
    def classify_category(self, title: str, content: str, categories: List[Dict[str, str]]) -> Optional[str]:
        """
        Classify article into a category using AI
        
        Args:
            title: Article title
            content: Article content
            categories: List of dicts with 'id', 'name', 'slug' keys
            
        Returns:
            Category slug if match found, None otherwise
        """
        return self.provider.classify_category(title, content, categories)
    
    def classify_categories_batch(self, articles: List[Dict[str, str]], categories: List[Dict[str, str]]) -> List[Optional[str]]:
        """
        Classify multiple articles into categories in batch
        
        Args:
            articles: List of dicts with 'title' and 'content' keys
            categories: List of dicts with 'id', 'name', 'slug' keys
            
        Returns:
            List of category slugs (or None) in the same order as input articles
        """
        return self.provider.classify_categories_batch(articles, categories)
    
    def summarize_and_classify_batch(self, articles: List[Dict[str, str]], categories: List[Dict[str, str]], max_length: int = 200) -> List[Dict[str, Optional[str]]]:
        """
        Summarize and classify categories for multiple articles in a single batch query
        
        Args:
            articles: List of dicts with 'title' and 'content' keys
            categories: List of dicts with 'id', 'name', 'slug' keys
            max_length: Maximum length of each summary
            
        Returns:
            List of dicts with 'summary' and 'category_slug' keys in the same order as input articles
        """
        return self.provider.summarize_and_classify_batch(articles, categories, max_length)

