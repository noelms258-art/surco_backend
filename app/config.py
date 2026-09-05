import os

class Config:
    # Ruta de la base de datos
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATABASE = os.path.join(BASE_DIR, "BBDD.db")
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '8f1d9c7a2b4e6f0a9d3c5b7e1f4a6c8d')

    # Flask
    DEBUG = True

    # Opcional
    JSON_SORT_KEYS = False