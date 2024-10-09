import os

class Config:
    # Inne ustawienia
    MAIL_SERVER = 'smtp.sendgrid.net'  # Adres serwera SMTP
    MAIL_PORT = 587  # Port serwera SMTP
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = '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'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SECRET_KEY = 'site'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'site')  # Klucz do sesji
    DEBUG = os.getenv('DEBUG', True)  # Ustawienia debugowania
