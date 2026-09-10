import os

class Settings:
    PROJECT_NAME: str = "MoneyFlow AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./moneyflow.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_jwt_key_for_moneyflow_fintech_change_in_production_98374")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    AI_PROVIDER: str = "mock"
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    DEFAULT_CURRENCY: str = "INR"
    DEFAULT_CURRENCY_SYMBOL: str = "₹"

settings = Settings()
