from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic IT Helpdesk"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:3000"

    database_url: str = "sqlite:///./agentic_helpdesk.db"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_chat_deployment: str = ""
    azure_openai_embedding_deployment: str = ""

    llm_temperature: float = 0.2
    llm_max_tokens: int = 1000

    vector_store: Literal["chroma", "azure_ai_search"] = "chroma"
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "it_helpdesk_kb"

    servicenow_mode: Literal["real", "mock"] = "mock"
    servicenow_instance_url: str = ""
    servicenow_username: str = ""
    servicenow_password: str = ""

    demo_employee_email: str = "employee@example.com"
    demo_admin_email: str = "admin@example.com"

    log_level: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()