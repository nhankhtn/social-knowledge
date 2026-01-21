from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # AI Service - Gemini
    gemini_api_key: str
    
    # Discord
    discord_bot_token: Optional[str] = None
    discord_channel_id: Optional[str] = None
    
    # Scheduler
    crawl_at_hours: str = "0,8,16"
    crawl_at_minutes: str = "0"
    timezone: str = "Asia/Ho_Chi_Minh"
    
    # AI Batch Processing
    summary_batch_size: int = 5  # Number of articles per batch for summarization
    
    # Crawler Settings
    crawl_articles_limit: int = 30  # Maximum number of articles to crawl per source per run
    
    # Logging
    log_level: str = "INFO"
    
    # Swagger UI Authentication
    swagger_username: str = "admin"
    swagger_password: str = "1012"
    
    # Rate Limiting
    rate_limit_per_minute: int = 30  # Requests per minute per user/IP
    rate_limit_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

