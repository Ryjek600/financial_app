from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

from extensions import db, mail  # Importuj z extensions.py

migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Ładowanie konfiguracji z folderu `instance`
    app.config.from_object('config.Config')  # Konfiguracja z pliku głównego
    app.config.from_pyfile('config.py')       # Konfiguracja z folderu `instance`
    
    # Inicjalizacja bazy danych, migracji i maila
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    with app.app_context():
        # Import routes
        from routes.main_routes import main
        app.register_blueprint(main)

        # Debugowanie: Sprawdź, czy tabele są obecne
        try:
            tables = db.engine.table_names()
            print(f"Tables in the database: {tables}")
        except Exception as e:
            print(f"Error retrieving tables: {e}")

        # Create tables if they don't exist
        try:
            db.create_all()
            print("All tables created.")
        except Exception as e:
            print(f"Error creating tables: {e}")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)










