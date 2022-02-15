from flask import Flask
from flask_graphql_auth import GraphQLAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from Spill_Backend_App.API.config import Config


db = SQLAlchemy()
migrate = Migrate()
graph_auth = GraphQLAuth()


def create_app(config_class=None):
    from Spill_Backend_App.API.routes import bp as route_bp

    if config_class is None:
        raise ValueError("A Config Class Must Be Provided to 'create_app'")
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    graph_auth.init_app(app)
    app.register_blueprint(route_bp)

    return app
