import os
import json
import uuid
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, jsonify, g, request

from app.config import Config
from app.extensions import db, migrate
from app.routes import event_bp

# =====================================================
# 🚀 SENTRY
# =====================================================
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def init_sentry():
    dsn = os.environ.get("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )


# =====================================================
# 🔧 BUILD INFO (READ ONLY)
# =====================================================
def get_build_info():
    try:
        with open("build_info.json") as f:
            return json.load(f)
    except Exception:
        return {
            "version": "unknown",
            "commit": "unknown",
            "branch": "unknown",
            "build_time_utc": "unknown",
            "build_time_ist": "unknown"
        }


# =====================================================
# 🧾 LOG FORMATTER
# =====================================================
class RequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.request_id = getattr(g, "request_id", "N/A")
        except RuntimeError:
            record.request_id = "N/A"

        return super().format(record)


# =====================================================
# 🚀 APP FACTORY
# =====================================================
def create_app(testing: bool = False):
    app = Flask(__name__)

    # These are commented out debug prints to avoid cluttering logs,
    # but can be uncommented for troubleshooting:-
    # print("TEST-123")
    # print("CWD =", repr(os.getcwd()))
    # print("TEST-456")

    app.config.from_object(Config)

    if testing:
        app.config["TESTING"] = True

    init_sentry()

    # =====================================================
    # 🌐 CORS
    # =====================================================
    from flask_cors import CORS

    CORS(app)

    # =====================================================
    # 🔗 EXTENSIONS
    # =====================================================
    db.init_app(app)
    migrate.init_app(app, db)

    # =====================================================
    # 🆔 REQUEST ID
    # =====================================================
    @app.before_request
    def assign_request_id():
        g.request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4())
        )

    @app.after_request
    def attach_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        return response

    # =====================================================
    # 📂 LOGGING
    # =====================================================
    logs_path = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_path, exist_ok=True)

    handler = TimedRotatingFileHandler(
        os.path.join(logs_path, "events.log"),
        when="midnight",
        backupCount=30,
        encoding="utf-8"
    )

    handler.setFormatter(
        RequestFormatter(
            "%(asctime)s [%(levelname)s] [REQ:%(request_id)s] %(message)s"
        )
    )

    app.logger.addHandler(handler)

    stream_handler = logging.StreamHandler()

    stream_handler.setFormatter(
        RequestFormatter(
            "%(asctime)s [%(levelname)s] [REQ:%(request_id)s] %(message)s"
        )
    )

    app.logger.addHandler(stream_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    # =====================================================
    # 📦 ROUTES
    # =====================================================
    app.register_blueprint(
        event_bp,
        url_prefix="/api/v1"
    )

    # =====================================================
    # ❤️ HEALTH (HTML + JSON)
    # =====================================================
    @app.get("/")
    def health():
        info = get_build_info()

        # HTML (browser)
        if "text/html" in request.headers.get("Accept", ""):
            return f"""
            <html>
            <head>
                <title>🚀 ML Events Service</title>
                <style>
                    body {{
                        font-family: Arial;
                        background: #0f172a;
                        color: white;
                        text-align: center;
                        padding-top: 60px;
                    }}
                    .card {{
                        background: #1e293b;
                        padding: 30px;
                        border-radius: 12px;
                        display: inline-block;
                        box-shadow: 0 0 20px rgba(0,0,0,0.5);
                    }}
                    h1 {{
                        color: #38bdf8;
                    }}
                    .ok {{
                        color: #22c55e;
                    }}
                    .label {{
                        color: #94a3b8;
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>🚀 ML Events Service</h1>
                    <p class="ok">🟢 UP</p>

                    <p><span class="label">Version:</span> {info.get("version")}</p>
                    <p><span class="label">Commit:</span> {info.get("commit")}</p>
                    <p><span class="label">Branch:</span> {info.get("branch")}</p>
                    <p><span class="label">UTC:</span> {info.get("build_time_utc")}</p>
                    <p><span class="label">IST:</span> {info.get("build_time_ist")}</p>
                </div>
            </body>
            </html>
            """, 200

        # JSON (API)
        return jsonify({
            "status": "ml-events-service UP",
            "build": info
        }), 200

    # =====================================================
    # ❤️ HEALTH ENDPOINT (FOR RENDER/CD)
    # =====================================================
    @app.get("/health")
    def health_check():
        return jsonify({
            "status": "UP",
            "service": "ml-events-service",
            "build": get_build_info()
        }), 200

    return app
