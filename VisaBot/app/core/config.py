"""
Application configuration settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Project info
    PROJECT_NAME: str = "VisaBot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
    
    # OpenAI settings (primary LLM service)
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # Using cheaper model
    OPENAI_EVALUATION_MODEL: str = "gpt-3.5-turbo"  # Using cheaper model for evaluation too
    OPENAI_MAX_TOKENS: int = 1500  # Reduced token limit to save costs
    OPENAI_TEMPERATURE: float = 0.7
    
    # Groq settings (optional - keeping for backward compatibility)
    GROQ_API_KEY: Optional[str] = None
    GROQ_DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_EVALUATION_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 2000
    GROQ_TEMPERATURE: float = 0.7
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # Database settings (optional)
    DATABASE_URL: Optional[str] = None
    DB_ENGINE: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    SERVICE_KEY: Optional[str] = None
    JWT_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "visabot.log"
    
    # Bot settings
    BOT_SESSION_TIMEOUT: int = 3600  # 1 hour in seconds
    MAX_CONVERSATION_HISTORY: int = 10
    
    # File upload settings (optional)
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    # Security settings (optional)
    SECRET_KEY: str = "your_secret_key_here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @validator("OPENAI_API_KEY")
    def validate_openai_key(cls, v):
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env file


# Create settings instance
settings = Settings() 