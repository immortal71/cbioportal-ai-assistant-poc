"""
Configuration file for cBioPortal AI Assistant
Author: Aashish Kharel
GSoC 2026
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Application configuration"""
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")  # or "openai" or "gemini" or "ollama" or "groq"
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # LLM Model Selection
    CLAUDE_MODEL: str = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    GROQ_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    OLLAMA_MODEL: str = os.getenv("LLM_MODEL", "llama3.1:8b")
    
    # Confidence Thresholds
    MIN_CONFIDENCE_SCORE: float = 5.0  # Out of 10
    
    # cBioPortal API
    CBIOPORTAL_API_URL: str = "https://www.cbioportal.org/api"
    
    # Fallback Settings
    USE_PATTERN_FALLBACK: bool = True
    
    @classmethod
    def is_llm_configured(cls) -> bool:
        """Check if LLM is properly configured"""
        if cls.LLM_PROVIDER == "anthropic":
            return cls.ANTHROPIC_API_KEY is not None
        elif cls.LLM_PROVIDER == "openai":
            return cls.OPENAI_API_KEY is not None
        elif cls.LLM_PROVIDER == "gemini":
            return cls.GEMINI_API_KEY is not None
        elif cls.LLM_PROVIDER == "groq":
            return cls.GROQ_API_KEY is not None
        elif cls.LLM_PROVIDER == "ollama":
            return True  # Ollama runs locally, no API key needed
        return False
