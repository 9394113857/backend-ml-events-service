# =====================================================
# ML EVENTS SERVICE – APP FACTORY (FINAL CLEAN ✅) 
# =====================================================

import os
import json
import uuid
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, jsonify, g, request
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate
from app.routes import event_bp


def get_build_info():
    try:
        with open("build_info.json") as f:
            return json.load(f)
    except Exception as e:
        return {
            "version": "unknown",
            "commit": "unknown",
            "branch": "unknown",
            "build_time_utc": "unknown",
            "build_time_ist": "unknown",
            "error": str(e)
        }


class RequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.request_id = getattr(g, "request_id", "N/A")
        except RuntimeError:
            record.request_id = "N/A"
        return super().format(record)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ FIXED CORS (ALLOW ALL ROUTES)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.before_request
    def assign_request_id():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    @app.after_request
    def attach_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        return response

    # Logging
    logs_path = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_path, exist_ok=True)

    handler = TimedRotatingFileHandler(
        os.path.join(logs_path, "events.log"),
        when="midnight",
        backupCount=30,
        encoding="utf-8"
    )

    handler.setFormatter(RequestFormatter(
        "%(asctime)s [%(levelname)s] [REQ:%(request_id)s] %(message)s"
    ))

    if not app.logger.handlers:
        app.logger.addHandler(handler)

    app.logger.setLevel(logging.INFO)

    # ✅ CLEAN ROUTE PREFIX
    app.register_blueprint(event_bp, url_prefix="/api/v1")

    @app.get("/")
    def health():
        return jsonify({
            "status": "ml-events-service UP",
            "build": get_build_info()
        }), 200

    return app
