import google.generativeai as genai
from typing import Optional

from ....config.settings import settings


class GeminiProvider:
    """Gemini AI provider for summarization"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def summarize(self, content: str, max_length: int = 200) -> str:
        """
        Summarize content using Gemini
        
        Args:
            content: Article content to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summary text
        """
        prompt = f"""Hãy tóm tắt bài báo sau đây một cách ngắn gọn và súc tích (tối đa {max_length} từ):

{content}

Tóm tắt:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

