"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for the B2AI Agentic Commerce Protocol."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "B2AI Agentic Commerce Protocol"
    environment: str = "development"
    database_url: str = "sqlite:///./b2ai.db"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- AI / Agent ---
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    agent_provider: str = "openai"  # "openai" | "bedrock" | "mock"
    auto_approve: bool = True  # if True, skip human-in-the-loop confirmation (demo)
    
    # --- AWS Bedrock (optional) ---
    bedrock_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # --- Agent Memory ---
    memory_file_path: str = "./.agent_memory.json"
    memory_enabled: bool = True

    # --- Avalanche Fuji (XSGD settlement) ---
    avalanche_rpc_url: str = ""
    xsgd_contract_address: str = ""
    settlement_private_key: str = ""
    settlement_network: str = "Avalanche Fuji C-Chain"
    chain_id: int = 43113
    simulate_settlement: bool = False  # if True, never hit the chain

    # --- Policy defaults ---
    default_max_transaction: float = 100.0
    default_daily_limit: float = 500.0
    default_currency: str = "XSGD"
    default_allowed_merchants: str = "Nike,Amazon,Apple"

    @property
    def allowed_merchants(self) -> list[str]:
        return [m.strip() for m in self.default_allowed_merchants.split(",") if m.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()