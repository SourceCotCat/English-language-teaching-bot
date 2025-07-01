import os
from dotenv import load_dotenv


load_dotenv() # загружаем переменные из .env файла


TOKEN = os.getenv("TOKEN")


DB_CONFIG = {
    'dbname': os.getenv("DB_NAME"),       # Название БД
    'user': os.getenv("DB_USER"),         # Пользователь БД 
    'password': os.getenv("DB_PASSWORD"), # Пароль пользователя
    'host': os.getenv("DB_HOST"),         # Хост 
    'port': int(os.getenv("DB_PORT")),    # Порт 
}