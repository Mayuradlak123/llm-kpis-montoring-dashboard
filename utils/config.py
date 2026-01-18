"""
Configuration management using Pydantic Settings.
Loads environment variables with type validation.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable loading."""
    
    # Groq LLM Configuration
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    
    # MongoDB Configuration (using existing env var names)
    mongo_connection_string: str
    db_name: str = "LLM_KPI_MONITORING"
    
    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "llm_kpi_monitoring"
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    
    # Cost Tracking (USD per 1M tokens)
    groq_cost_per_1m_input_tokens: float = 0.59
    groq_cost_per_1m_output_tokens: float = 0.79
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Provide aliases for backward compatibility
    @property
    def mongodb_uri(self) -> str:
        """Alias for mongo_connection_string."""
        return self.mongo_connection_string
    
    @property
    def mongodb_database(self) -> str:
        """Alias for db_name."""
        return self.db_name


# Global settings instance
settings = Settings()
