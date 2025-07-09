import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from init import words 

load_dotenv() # загружаем переменные из .env файла

DB_CONFIG = {
    'dbname': os.getenv("DB_NAME"),       # Название БД
    'user': os.getenv("DB_USER"),         # Пользователь БД 
    'password': os.getenv("DB_PASSWORD"), # Пароль пользователя
    'host': os.getenv("DB_HOST"),         # Хост 
    'port': int(os.getenv("DB_PORT")),    # Порт 
    'token': os.getenv("TOKEN"),          # токен бота
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
               f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_bd():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        words(db)
