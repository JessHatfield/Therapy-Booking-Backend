from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from API.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):

    from API.routes import bp as route_bp

    if config_class is None:
        raise ValueError("A Config Class Must Be Provided to 'create_app'")
    app=Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app,db)
    app.register_blueprint(route_bp)

    return app


