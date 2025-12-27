from typing import Optional
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

