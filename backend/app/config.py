import os
from dotenv import load_dotenv

# chargement du env

load_dotenv()


class config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'lepro1234'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("SECRET_KEY")

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'testeurX237@gmail.com'
    MAIL_PASSWORD = 'xics xqle srki ykjz '
    MAIL_DEFAULT_SENDER = 'sofodidierbrassy@gmail.com'
