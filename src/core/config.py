from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM7 Configuration (OpenAI-compatible API)
    llm7_token: str = os.getenv("LLM7_TOKEN", "")
    llm7_base_url: str = "https://api.llm7.io/v1"
    llm7_text_model: str = "open-mixtral-8x22b"  # Best for text-based recipe generation
    llm7_image_model: str = "gpt-4o-mini-2024-07-18"  # Best for image processing
    
    # Legacy OpenAI Configuration (kept for fallback)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-3.5-turbo"
    
    # Gemini Configuration (optional fallback)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = "gemini-1.5-flash"
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Application Configuration
    app_name: str = "Recipe Generator API"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered recipe generation from ingredients"
    
    # CORS Configuration
    allowed_origins: list = ["*"]
    allowed_methods: list = ["*"]
    allowed_headers: list = ["*"]
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
