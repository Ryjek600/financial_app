import os

class Config:
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.getenv('SENDGRID_API_KEY')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'site')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('DEBUG', True)

    # Ustawienia dla Flask-Mail
    MAIL_DEBUG = os.getenv('MAIL_DEBUG', 'False').lower() == 'true'  # Zmiana tutaj

