from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # AI Service - Gemini
    gemini_api_key: str
    
    # Firebase (optional - for token verification)
    firebase_project_id: Optional[str] = None
    
    # Discord
    discord_bot_token: Optional[str] = None
    discord_channel_id: Optional[str] = None
    
    # Scheduler
    crawl_interval_hours: int = 8
    timezone: str = "Asia/Ho_Chi_Minh"
    
    # AI Batch Processing
    summary_batch_size: int = 5  # Number of articles per batch for summarization
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

