import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class NotificationSender:
    """Send notifications to different providers"""
    
    async def send(self, provider: str, credentials: Dict[str, Any], 
                   title: str, summary: str, url: str, source_name: str, category_name: Optional[str] = None) -> Optional[str]:
        """
        Send notification based on provider type
        
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            if provider == "discord_webhook":
                return await self._send_discord_webhook(credentials, title, summary, url, source_name, category_name)
            elif provider == "telegram_bot":
                return await self._send_telegram(credentials, title, summary, url, source_name, category_name)
            elif provider == "slack_webhook":
                return await self._send_slack_webhook(credentials, title, summary, url, source_name, category_name)
            else:
                logger.warning(f"Unknown provider: {provider}")
                return None
        except Exception as e:
            logger.error(f"Error sending notification via {provider}: {e}")
            return None
    
    async def _send_discord_webhook(self, credentials: Dict[str, Any], 
                                     title: str, summary: str, url: str, source_name: str, category_name: Optional[str] = None) -> Optional[str]:
        """Send via Discord webhook"""
        webhook_url = credentials.get("url")
        if not webhook_url:
            logger.error("Discord webhook URL not found in credentials")
            return None
        
        fields = [
            {"name": "Nguồn", "value": source_name, "inline": True}
        ]
        
        if category_name:
            fields.append({"name": "Thể loại", "value": category_name, "inline": True})
        
        embed = {
            "title": title[:256],
            "description": summary[:4096],
            "color": 0x5865F2,
            "url": url,
            "fields": fields,
            "footer": {"text": "Social Knowledge Bot"}
        }
        
        payload = {"embeds": [embed]}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            if response.status_code in [200, 204]:
                logger.info(f"Sent notification to Discord webhook")
                return str(response.headers.get("x-message-id", ""))
            else:
                logger.error(f"Discord webhook failed: {response.status_code} - {response.text}")
                return None
    
    async def _send_telegram(self, credentials: Dict[str, Any], 
                             title: str, summary: str, url: str, source_name: str, category_name: Optional[str] = None) -> Optional[str]:
        """Send via Telegram bot"""
        token = credentials.get("token")
        chat_id = credentials.get("chat_id")
        
        if not token or not chat_id:
            logger.error("Telegram token or chat_id not found in credentials")
            return None
        
        category_text = f"\n🏷️ Thể loại: {category_name}" if category_name else ""
        message = f"*{title}*\n\n{summary}\n\n🔗 [Xem thêm]({url})\n📰 Nguồn: {source_name}{category_text}"
        
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"Sent notification to Telegram chat {chat_id}")
                return str(message_id) if message_id else None
            else:
                logger.error(f"Telegram send failed: {response.status_code} - {response.text}")
                return None
    
    async def _send_slack_webhook(self, credentials: Dict[str, Any], 
                                   title: str, summary: str, url: str, source_name: str, category_name: Optional[str] = None) -> Optional[str]:
        """Send via Slack webhook"""
        webhook_url = credentials.get("url")
        if not webhook_url:
            logger.error("Slack webhook URL not found in credentials")
            return None
        
        context_elements = [
            {"type": "mrkdwn", "text": f"📰 *Nguồn:* {source_name}"}
        ]
        if category_name:
            context_elements.append({"type": "mrkdwn", "text": f"🏷️ *Category:* {category_name}"})
        
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": title[:150]}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": summary}
                },
                {
                    "type": "context",
                    "elements": context_elements
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Xem thêm"},
                            "url": url
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            if response.status_code == 200:
                logger.info(f"Sent notification to Slack webhook")
                return "slack_message"
            else:
                logger.error(f"Slack webhook failed: {response.status_code} - {response.text}")
                return None
