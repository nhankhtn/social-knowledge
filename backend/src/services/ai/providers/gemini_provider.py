import google.generativeai as genai
from typing import Optional, List, Dict
import json
import re
import logging

from ....config.settings import settings

logger = logging.getLogger(__name__)


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
    
    def summarize_batch(self, articles: List[Dict[str, str]], max_length: int = 200) -> List[str]:
        """
        Summarize multiple articles in batch using Gemini
        
        Args:
            articles: List of dicts with 'title' and 'content' keys
            max_length: Maximum length of each summary
            
        Returns:
            List of summary texts in the same order as input articles
        """
        if not articles:
            return []
        
        # Build batch prompt
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            content = article.get('content', '')
            articles_text += f"\n\n=== BÀI {i} ===\n"
            articles_text += f"Tiêu đề: {title}\n"
            articles_text += f"Nội dung: {content}\n"
        
        prompt = f"""Hãy tóm tắt {len(articles)} bài báo sau đây. Mỗi bài tóm tắt ngắn gọn và súc tích (tối đa {max_length} từ).

Trả về kết quả theo định dạng JSON sau (chính xác format này):
{{
  "summaries": [
    {{"id": 1, "summary": "tóm tắt bài 1"}},
    {{"id": 2, "summary": "tóm tắt bài 2"}},
    ...
  ]
}}

{articles_text}

Chỉ trả về JSON, không có text thêm:"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON response
            result = json.loads(response_text)
            summaries = result.get('summaries', [])
            
            # Sort by id to ensure correct order
            summaries.sort(key=lambda x: x.get('id', 0))
            
            # Extract summary texts
            summary_texts = [s.get('summary', '') for s in summaries]
            
            # If we got fewer summaries than articles, pad with empty strings
            while len(summary_texts) < len(articles):
                summary_texts.append('')
            
            return summary_texts[:len(articles)]
            
        except json.JSONDecodeError as e:
            # Fallback: try to parse line by line if JSON fails
            logger.warning(f"Failed to parse JSON response, trying fallback: {e}")
            lines = response_text.split('\n')
            summaries = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('{') and not line.startswith('}'):
                    # Try to extract summary text
                    if 'summary' in line.lower() or len(line) > 20:
                        summaries.append(line)
            
            # Pad to match article count
            while len(summaries) < len(articles):
                summaries.append('')
            
            return summaries[:len(articles)]
            
        except Exception as e:
            raise Exception(f"Gemini batch API error: {str(e)}")

