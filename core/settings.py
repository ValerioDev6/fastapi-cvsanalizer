import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # App
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Openai api key

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")


settings = Settings()
