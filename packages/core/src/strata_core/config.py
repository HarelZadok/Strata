from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gateway_host: str = "127.0.0.1"
    gateway_port: int = 8000
    grpc_port: int = 50051
    llm_provider_mode: str = "local" # local, cloud, remote
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str | None = None
    llm_model: str = "qwen2.5:7b"

    class Config:
        env_prefix = "STRATA_"

settings = Settings()
