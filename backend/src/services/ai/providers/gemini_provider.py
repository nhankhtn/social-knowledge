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
        if not articles:
            return []
        
        # Build categories list for prompt
        categories_text = "\n".join([
            f"- {cat['name']} (slug: {cat['slug']})" 
            for cat in categories
        ]) if categories else "Không có thể loại nào"
        
        # Build articles text
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            content = article.get('content', '')
            articles_text += f"\n\n=== BÀI {i} ===\n"
            articles_text += f"Tiêu đề: {title}\n"
            articles_text += f"Nội dung: {content[:1500]}\n"  # Limit content length
        
        prompt = f"""Hãy tóm tắt và phân loại {len(articles)} bài báo sau đây.

Các thể loại có sẵn:
{categories_text}

{articles_text}

Với mỗi bài báo, hãy:
1. Tóm tắt ngắn gọn và súc tích (tối đa {max_length} từ)
2. Phân loại vào một thể loại phù hợp nhất (trả về slug của thể loại, hoặc null nếu không có thể loại nào phù hợp)

Trả về kết quả theo định dạng JSON sau (chính xác format này):
{{
  "results": [
    {{"id": 1, "summary": "tóm tắt bài 1", "category_slug": "cong-nghe"}},
    {{"id": 2, "summary": "tóm tắt bài 2", "category_slug": "the-thao"}},
    {{"id": 3, "summary": "tóm tắt bài 3", "category_slug": null}},
    ...
  ]
}}

Chỉ trả về JSON, không có text thêm:"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON response
            result = json.loads(response_text)
            results = result.get('results', [])
            
            # Sort by id to ensure correct order
            results.sort(key=lambda x: x.get('id', 0))
            
            # Extract summaries and category slugs
            processed_results = []
            for res in results:
                summary = res.get('summary', '')
                category_slug = res.get('category_slug')
                
                # Validate category slug exists
                if category_slug and category_slug.lower() != "null":
                    # Verify slug exists in categories
                    found = False
                    for cat in categories:
                        if cat['slug'].lower() == category_slug.lower():
                            processed_results.append({
                                'summary': summary,
                                'category_slug': cat['slug']
                            })
                            found = True
                            break
                    if not found:
                        processed_results.append({
                            'summary': summary,
                            'category_slug': None
                        })
                else:
                    processed_results.append({
                        'summary': summary,
                        'category_slug': None
                    })
            
            # Pad to match article count
            while len(processed_results) < len(articles):
                processed_results.append({
                    'summary': '',
                    'category_slug': None
                })
            
            return processed_results[:len(articles)]
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse summarize_and_classify JSON response: {e}")
            # Fallback: return empty results
            return [{'summary': '', 'category_slug': None}] * len(articles)
        except Exception as e:
            logger.error(f"Error in summarize_and_classify_batch: {e}")
            return [{'summary': '', 'category_slug': None}] * len(articles)
    
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
        if not categories:
            return None
        
        # Build categories list for prompt
        categories_text = "\n".join([
            f"- {cat['name']} (slug: {cat['slug']})" 
            for cat in categories
        ])
        
        prompt = f"""Hãy phân loại bài báo sau vào một trong các thể loại dưới đây dựa trên nội dung và tiêu đề.

Các thể loại có sẵn:
{categories_text}

Tiêu đề: {title}

Nội dung: {content[:2000]}

Hãy chọn thể loại phù hợp nhất. Chỉ trả về slug của thể loại (ví dụ: "cong-nghe", "the-thao"), không có text thêm. Nếu không có thể loại nào phù hợp, trả về "null"."""
        
        try:
            response = self.model.generate_content(prompt)
            category_slug = response.text.strip().strip('"').strip("'")
            
            # Check if the returned slug exists in categories
            if category_slug and category_slug.lower() != "null":
                # Find matching category
                for cat in categories:
                    if cat['slug'].lower() == category_slug.lower():
                        return cat['slug']
            
            return None
        except Exception as e:
            logger.error(f"Error classifying category: {e}")
            return None
    
    def classify_categories_batch(self, articles: List[Dict[str, str]], categories: List[Dict[str, str]]) -> List[Optional[str]]:
        """
        Classify multiple articles into categories in batch
        
        Args:
            articles: List of dicts with 'title' and 'content' keys
            categories: List of dicts with 'id', 'name', 'slug' keys
            
        Returns:
            List of category slugs (or None) in the same order as input articles
        """
        if not articles or not categories:
            return [None] * len(articles)
        
        # Build categories list for prompt
        categories_text = "\n".join([
            f"- {cat['name']} (slug: {cat['slug']})" 
            for cat in categories
        ])
        
        # Build articles text
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            content = article.get('content', '')
            articles_text += f"\n\n=== BÀI {i} ===\n"
            articles_text += f"Tiêu đề: {title}\n"
            articles_text += f"Nội dung: {content[:1000]}\n"  # Limit content length
        
        prompt = f"""Hãy phân loại {len(articles)} bài báo sau vào các thể loại dưới đây dựa trên nội dung và tiêu đề.

Các thể loại có sẵn:
{categories_text}

{articles_text}

Trả về kết quả theo định dạng JSON sau (chính xác format này):
{{
  "classifications": [
    {{"id": 1, "category_slug": "cong-nghe"}},
    {{"id": 2, "category_slug": "the-thao"}},
    {{"id": 3, "category_slug": null}},
    ...
  ]
}}

Nếu không có thể loại nào phù hợp, trả về null cho category_slug. Chỉ trả về JSON, không có text thêm:"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON response
            result = json.loads(response_text)
            classifications = result.get('classifications', [])
            
            # Sort by id to ensure correct order
            classifications.sort(key=lambda x: x.get('id', 0))
            
            # Extract category slugs
            category_slugs = []
            for cls in classifications:
                slug = cls.get('category_slug')
                if slug and slug.lower() != "null":
                    # Verify slug exists in categories
                    found = False
                    for cat in categories:
                        if cat['slug'].lower() == slug.lower():
                            category_slugs.append(cat['slug'])
                            found = True
                            break
                    if not found:
                        category_slugs.append(None)
                else:
                    category_slugs.append(None)
            
            # Pad to match article count
            while len(category_slugs) < len(articles):
                category_slugs.append(None)
            
            return category_slugs[:len(articles)]
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse classification JSON response: {e}")
            return [None] * len(articles)
        except Exception as e:
            logger.error(f"Error classifying categories batch: {e}")
            return [None] * len(articles)

