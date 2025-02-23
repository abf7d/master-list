## config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    TENANT_ID: Optional[str] = None
    AUDIENCE: Optional[str] = None
    JWKS_URL: Optional[str] = None
    AZURE_AD_CLIENT_ID: Optional[str] = None
    AZURE_AD_CLIENT_SECRET: Optional[str] = None
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"

settings = Settings()