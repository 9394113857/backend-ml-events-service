from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate
from app.routes import event_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------------------------------------
    # Enable CORS (Angular / Frontend access)
    # ---------------------------------------------
    CORS(app)

    # ---------------------------------------------
    # Initialize Extensions
    # ---------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)

    # ---------------------------------------------
    # Register Blueprints
    # ---------------------------------------------
    # Health check:  GET /health
    # Events API:    POST /api/events
    # Events List:   GET  /api/events
    app.register_blueprint(event_bp)

    return app
