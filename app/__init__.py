# =====================================================
# 🚀 ML EVENTS SERVICE – APP FACTORY (FINAL PRODUCTION)
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



# =====================================================
# 🔧 BUILD INFO
# =====================================================

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




# =====================================================
# 🧾 LOG FORMATTER
# =====================================================

class RequestFormatter(logging.Formatter):

    def format(self, record):

        try:

            record.request_id = getattr(
                g,
                "request_id",
                "N/A"
            )

        except RuntimeError:

            record.request_id = "N/A"


        return super().format(record)




# =====================================================
# 🚀 APP FACTORY
# =====================================================

def create_app(testing=False):


    app = Flask(__name__)


    app.config.from_object(Config)



    if testing:

        app.config["TESTING"] = True




    # =====================================================
    # 🌐 CORS
    # =====================================================

    CORS(app)




    # =====================================================
    # 🔗 EXTENSIONS
    # =====================================================

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )




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

    logs_path = os.path.join(

        os.getcwd(),

        "logs"

    )


    os.makedirs(

        logs_path,

        exist_ok=True

    )



    handler = TimedRotatingFileHandler(

        os.path.join(

            logs_path,

            "events.log"

        ),

        when="midnight",

        backupCount=30,

        encoding="utf-8"

    )



    handler.setFormatter(

        RequestFormatter(

            "%(asctime)s "
            "[%(levelname)s] "
            "[REQ:%(request_id)s] "
            "%(message)s"

        )

    )



    if not app.logger.handlers:

        app.logger.addHandler(handler)



    app.logger.setLevel(logging.INFO)





    # =====================================================
    # 📦 ROUTES
    # =====================================================

    app.register_blueprint(

        event_bp,

        url_prefix="/api/v1"

    )






    # =====================================================
    # ❤️ CD HEALTH CHECK
    # =====================================================

    @app.get("/health")

    def health_check():


        return jsonify({

            "status": "UP",

            "service": "ml-events-service",

            "build": get_build_info()

        }), 200





    # =====================================================
    # 🌐 ROOT HEALTH
    # =====================================================

    @app.get("/")

    def health():


        info = get_build_info()


        return jsonify({

            "status":

            "ml-events-service UP",


            "build":

            info

        }), 200





    return app
