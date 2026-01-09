import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ml-events-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///ml_events.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
