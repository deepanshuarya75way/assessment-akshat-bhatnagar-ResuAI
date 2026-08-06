from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    APP_NAME = "Placement Copilot"
    DATABASE_URL = os.getenv("DATABASE_URL")

    VERSION = "1.0"

settings = Settings()