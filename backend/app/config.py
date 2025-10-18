"""
Configuration settings for the Generative AI Chatbot.
Maps environment variables from .env to strongly-typed settings using Pydantic v2.
"""
from functools import lru_cache
from typing import Optional, List
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),  # Project root .env
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars instead of erroring
    )

    # Application Info
    app_name: str = "Suyash GenAI Chatbot"
    app_version: str = "1.0.0"
    environment: str = Field(default="dev", description="Environment: dev|prod")
    debug: bool = False

    # API Configuration (aliases to match .env)
    api_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    api_port: int = Field(default=8000, alias="BACKEND_PORT")
    api_prefix: str = "/api/v1"
    api_key: Optional[str] = None

    # CORS Settings
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:8501", "http://localhost:3000"],
        alias="ALLOWED_ORIGINS",
    )

    # Allow comma-separated list for CORS origins in .env
    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Support both JSON array and comma-separated
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                # Let pydantic handle JSON list normally
                return v
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # Qdrant Configuration (aliases to .env)
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="genai_resources", alias="QDRANT_COLLECTION_NAME")
    memory_collection: str = Field(default="user_memory", alias="QDRANT_MEMORY_COLLECTION")
    embedding_dimension: int = Field(default=384, alias="EMBEDDING_DIMENSION")

    # Embeddings and LLM models
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    model_provider: str = Field(default="gemini", alias="LLM_PROVIDER",
                                 description="ollama|openai|gemini|anthropic|mistral")
    small_model: str = Field(default="gemini-1.5-flash", alias="LLM_MODEL")
    large_model: str = Field(default="gemini-1.5-pro")

    # API Keys for LLM providers (aliases to .env)
    gemini_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    mistral_api_key: Optional[str] = Field(default=None, alias="MISTRAL_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    # Web Scraping Configuration
    serpapi_api_key: Optional[str] = Field(default=None, alias="SERPAPI_KEY")
    max_scrape_results: int = Field(default=5, alias="WEB_SCRAPING_MAX_RESULTS")
    scraping_timeout: int = Field(default=30, alias="QDRANT_TIMEOUT")

    # Agent Configuration
    max_clarifying_questions: int = 3
    min_clarifying_questions: int = 2
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    hybrid_search_weight: float = 0.7

    # Memory Configuration
    session_timeout_minutes: int = Field(default=60, alias="SESSION_TIMEOUT_MINUTES")
    max_session_history: int = Field(default=50, alias="MAX_CONVERSATION_HISTORY")
    enable_long_term_memory: bool = Field(default=True, alias="MEMORY_ENABLED")

    # Evaluation Configuration
    enable_evaluation: bool = Field(default=True, alias="EVALUATION_ENABLED")
    log_metrics_path: str = Field(default="backend/app/evaluation/evaluation_metrics.csv")
    hallucination_threshold: float = 0.8
    relevance_threshold: float = 0.7

    # Prompt Optimization
    max_prompt_tokens: int = 4000
    enable_prompt_compression: bool = True
    enable_history_summarization: bool = True
    summarization_threshold: int = 10

    # Persona Configuration
    persona_name: str = "Suyash"
    persona_role: str = "Research Analyst specializing in Generative AI"
    persona_age: int = 28
    persona_background: str = "Master's from MIT, freelance AI consultant"

    # GenAI Keywords for relevance filtering
    genai_keywords: List[str] = [
        "generative ai", "genai", "llm", "large language model", "gpt", "gemini",
        "mistral", "llama", "claude", "transformer", "diffusion", "stable diffusion",
        "dall-e", "gan", "vae", "text-to-image", "nlp", "computer vision", "cv",
        "multimodal", "langchain", "langgraph", "crewai", "vector database",
        "qdrant", "embeddings", "rag", "prompt engineering", "hugging face",
        "pytorch", "tensorflow", "ai research", "machine learning", "deep learning"
    ]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()