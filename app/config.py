import os
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """Application settings."""
    APP_NAME: str = "Swym AI Social Media Content Agent"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/swym_social")
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # LinkedIn API
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")
    LINKEDIN_ACCESS_TOKEN: Optional[str] = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    # Twitter API
    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET: Optional[str] = os.getenv("TWITTER_ACCESS_SECRET")
    
    # Instagram API
    INSTAGRAM_CLIENT_ID: Optional[str] = os.getenv("INSTAGRAM_CLIENT_ID")
    INSTAGRAM_CLIENT_SECRET: Optional[str] = os.getenv("INSTAGRAM_CLIENT_SECRET")
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    
    # Storage settings
    STORAGE_BUCKET: Optional[str] = os.getenv("STORAGE_BUCKET")
    STORAGE_ACCESS_KEY: Optional[str] = os.getenv("STORAGE_ACCESS_KEY")
    STORAGE_SECRET_KEY: Optional[str] = os.getenv("STORAGE_SECRET_KEY")
    
    # Redis for Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Web scraping settings
    SCRAPE_INTERVAL: int = int(os.getenv("SCRAPE_INTERVAL", "3600"))
    
    # Content settings
    MAX_POSTS_PER_DAY: int = int(os.getenv("MAX_POSTS_PER_DAY", "5"))
    
    # Image generation
    IMAGE_OUTPUT_DIR: str = os.getenv("IMAGE_OUTPUT_DIR", "data/images")
    DEFAULT_IMAGE_SIZE: tuple = (1200, 630)  # Default size for social media images

# Instantiate settings
settings = Settings() 