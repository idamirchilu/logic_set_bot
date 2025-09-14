import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Telegram Bot
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Ollama (Free LLM)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_max_tokens: int = int(os.getenv("OLLAMA_MAX_TOKENS", "800"))
    ollama_temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./logic_bot.db")
    database_driver: str = os.getenv("DATABASE_DRIVER", "aiosqlite")
    
    # App Settings
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))
    cache_maxsize: int = int(os.getenv("CACHE_MAXSIZE", "100"))
    
    # Scoring
    points_correct_answer: int = int(os.getenv("POINTS_CORRECT_ANSWER", "10"))
    points_per_exercise: int = int(os.getenv("POINTS_PER_EXERCISE", "5"))
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        # Ollama is optional - will use fallback responses if not available
        if not self.ollama_base_url:
            print("Warning: OLLAMA_BASE_URL not set. Some features will be limited.")
        
        # Validate database URL format
        if self.database_url.startswith("postgresql://"):
            # Convert to asyncpg format
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif self.database_url.startswith("sqlite://"):
            # Convert to aiosqlite format
            self.database_url = self.database_url.replace("sqlite://", "sqlite+aiosqlite://")

config = Config()