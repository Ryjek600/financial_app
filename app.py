from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv()
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    with app.app_context():
        from routes.main_routes import main
        app.register_blueprint(main)

        try:
            tables = db.engine.table_names()
            print(f"Tables in the database: {tables}")
        except Exception as e:
            print(f"Error retrieving tables: {e}")

        try:
            db.create_all()
            print("All tables created.")
        except Exception as e:
            print(f"Error creating tables: {e}")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)











