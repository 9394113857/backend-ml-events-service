# =====================================================
# USER EVENT MODEL (FINAL - FLEXIBLE ✅)
# =====================================================

from datetime import datetime
from app.extensions import db


class UserEvent(db.Model):
    __tablename__ = "user_events"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=True)
    session_id = db.Column(db.String(100), nullable=False)

    event_type = db.Column(db.String(100), nullable=False)
    object_type = db.Column(db.String(100), nullable=True)
    object_id = db.Column(db.String(100), nullable=True)

    event_metadata = db.Column(db.JSON, nullable=True)

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f"<UserEvent type={self.event_type} object={self.object_id}>"