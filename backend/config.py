from pydantic_settings import BaseSettings
from os import getcwd as cwd

class Settings(BaseSettings):
    SECRET_KEY: str = ""
    MONGO_URL: str = ""
    MONGO_DB_NAME: str = ""
    CONFIDENCE_THRESHOLD: float = 0
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0
    GOOGLE_MAPS_API_KEY: str = ""
    class Config:
        env_file = f"{cwd()}/backend/.env"

settings = Settings()

