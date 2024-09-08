from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Ładowanie konfiguracji z folderu `instance`
    app.config.from_object('config.Config')  # Konfiguracja z pliku głównego
    app.config.from_pyfile('config.py')       # Konfiguracja z folderu `instance`
    
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import routes
        from routes.main_routes import main
        app.register_blueprint(main)

        # Create tables
        db.create_all()

    return app


if __name__ == "__main__":
    app.run(debug=True)






