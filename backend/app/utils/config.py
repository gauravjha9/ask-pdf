from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    API_VERSION: str

    class config:
        env_file = ".env"


settings = Settings()