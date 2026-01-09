from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate
from app.routes import event_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------------------------------------
    # CORS (Angular / Netlify / Local)
    # ---------------------------------------------
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ---------------------------------------------
    # Extensions
    # ---------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)

    # ---------------------------------------------
    # Routes
    # ---------------------------------------------
    app.register_blueprint(event_bp)

    # ---------------------------------------------
    # Root Health Check
    # GET /
    # ---------------------------------------------
    @app.get("/")
    def health():
        return jsonify({"status": "ML-Events-Service UP"}), 200

    return app
