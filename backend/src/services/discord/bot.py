import discord
from discord.ext import commands
from typing import Optional
import logging
import asyncio

from ...config.settings import settings

logger = logging.getLogger(__name__)


class DiscordBot:
    """Discord bot for sending notifications"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.discord_bot_token
        self.channel_id = settings.discord_channel_id
        self.intents = discord.Intents.default()
        # message_content intent not needed - bot only sends messages, doesn't read them
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)
        self._setup_events()
    
    def _setup_events(self):
        """Setup bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f"Discord bot logged in as {self.bot.user}")
    
    async def send_summary(self, title: str, summary: str, url: str, source_name: str, category_name: Optional[str] = None) -> Optional[str]:
        """
        Send summary message to Discord channel
        
        Returns:
            Message ID if successful, None otherwise
        """
        if not self.token or not self.channel_id:
            logger.warning("Discord bot token or channel ID not configured")
            return None
        
        try:
            # Wait for bot to be ready (with timeout)
            max_wait = 30  # Maximum 30 seconds
            wait_time = 0
            while not self.bot.is_ready() and wait_time < max_wait:
                await asyncio.sleep(1)
                wait_time += 1
            
            if not self.bot.is_ready():
                logger.error("Discord bot not ready after waiting")
                return None
            
            # Parse channel_id - handle format: "channel_id" or "channel_id/thread_id"
            channel_id_str = str(self.channel_id).strip()
            if '/' in channel_id_str:
                parts = channel_id_str.split('/')
                channel_id = int(parts[0])
                thread_id = int(parts[1]) if len(parts) > 1 else None
            else:
                channel_id = int(channel_id_str)
                thread_id = None
            
            # Get channel
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found (bot may not have access)")
                return None
            
            # If thread_id is provided, get the thread
            if thread_id:
                try:
                    if hasattr(channel, 'get_thread'):
                        thread = channel.get_thread(thread_id)
                        if thread:
                            channel = thread
                        else:
                            logger.warning(f"Thread {thread_id} not found, using channel instead")
                    else:
                        logger.warning(f"Channel type does not support threads, using channel instead")
                except Exception as e:
                    logger.warning(f"Could not get thread {thread_id}: {e}, using channel instead")
            
            embed = discord.Embed(
                title=title[:256],  # Discord limit
                description=summary[:4096],  # Discord limit
                color=0x5865F2,
                url=url
            )
            embed.add_field(name="Nguồn", value=source_name, inline=True)
            if category_name:
                embed.add_field(name="Category", value=category_name, inline=True)
            embed.set_footer(text="Social Knowledge Bot")
            
            message = await channel.send(embed=embed)
            return str(message.id)
            
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            return None
    
    async def start(self):
        """Start the bot"""
        if self.token:
            await self.bot.start(self.token)
        else:
            logger.warning("Discord bot token not configured, bot will not start")
    
    async def close(self):
        """Close the bot"""
        await self.bot.close()

