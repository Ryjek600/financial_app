import os

class Config:
    # URI do bazy danych
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    
    # Zmniejsza obciążenie związane z monitorowaniem zmian w bazie danych
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Możesz dodać inne ustawienia konfiguracyjne tutaj
    SECRET_KEY = os.getenv('SECRET_KEY', 'site')  # Klucz do sesji
    DEBUG = os.getenv('DEBUG', True)  # Ustawienia debugowania
