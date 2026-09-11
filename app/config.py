import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '8f1d9c7a2b4e6f0a9d3c5b7e1f4a6c8d')

    DATABASE_URL = os.getenv("DATABASE_URL")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Opcional
    JSON_SORT_KEYS = False