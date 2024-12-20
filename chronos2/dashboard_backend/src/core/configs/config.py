from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    # JWT config
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 60 * 7
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    # Edge server
    EDGE_SERVER_IP: str
    EDGE_SERVER_PORT: str


settings = Settings()
