from datetime import datetime
from app.extensions import db


class UserEvent(db.Model):
    __tablename__ = "user_events"

    id = db.Column(db.Integer, primary_key=True)

    # Nullable for guest users
    user_id = db.Column(db.Integer, nullable=True)

    # Used to group events before login
    session_id = db.Column(db.String(100), nullable=False)

    # Event classification
    event_type = db.Column(db.String(50), nullable=False)   # view, click, add_to_cart
    object_type = db.Column(db.String(50), nullable=True)   # product, category, page
    object_id = db.Column(db.String(100), nullable=True)    # product_id, route name

    # 🔥 SAFE JSON FIELD (NOT "metadata")
    event_metadata = db.Column(db.JSON, nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<UserEvent "
            f"type={self.event_type} "
            f"object={self.object_type}:{self.object_id} "
            f"session={self.session_id}>"
        )
