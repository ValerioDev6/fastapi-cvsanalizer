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

    MAILER_SERVICE: str = os.getenv("MAILER_SERVICE")

    MAILER_EMAIL: str = os.getenv("MAILER_EMAIL")

    MAILER_PASSWORD: str = os.getenv("MAILER_PASSWORD")


settings = Settings()
