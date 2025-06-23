import os
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env
load_dotenv()

class Config:
    # Kunci rahasia untuk sesi Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-default-yang-kurang-aman'
    # URI database PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Menonaktifkan pelacakan modifikasi SQLAlchemy untuk menghemat memori
    SQLALCHEMY_TRACK_MODIFICATIONS = False