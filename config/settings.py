from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["anthropic", "openai", "google", "ollama", "openrouter"] = "ollama"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    openrouter_api_key: str = ""

    anthropic_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    google_model: str = "gemini-2.0-flash"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    ollama_model: str = "qwen3-coder:480b-cloud"
    ollama_base_url: str = "http://localhost:11434"

    max_validation_retries: int = 3
    output_dir: str = "./outputs"

    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "paper-to-notebook"

    @property
    def active_model(self) -> str:
        return {
            "anthropic": self.anthropic_model,
            "openai": self.openai_model,
            "google": self.google_model,
            "ollama": self.ollama_model,
            "openrouter": self.openrouter_model,
        }[self.llm_provider]


settings = Settings()