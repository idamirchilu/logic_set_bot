import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Telegram Bot
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Google API
    google_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./logic_bot.db")
    database_driver: str = os.getenv("DATABASE_DRIVER", "aiosqlite")
    
    # App Settings
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))
    cache_maxsize: int = int(os.getenv("CACHE_MAXSIZE", "100"))
    
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not os.getenv("OPENROUTER_API_KEY"):
            raise ValueError("OPENROUTER_API_KEY is required")
        # Ollama removed
        # Validate database URL format
        if self.database_url.startswith("postgresql://"):
            # Convert to asyncpg format
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif self.database_url.startswith("sqlite://"):
            # Convert to aiosqlite format
            self.database_url = self.database_url.replace("sqlite://", "sqlite+aiosqlite://")

config = Config()