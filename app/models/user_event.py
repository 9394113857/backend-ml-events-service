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
    event_type = db.Column(db.String(50), nullable=False)
    # examples: view_product, add_to_cart, checkout_started, order_placed

    object_type = db.Column(db.String(50), nullable=True)
    # examples: product, cart, order, page

    object_id = db.Column(db.String(100), nullable=True)
    # product_id, order_id, route name, etc.

    # JSON-safe metadata (price, quantity, totals, etc.)
    event_metadata = db.Column(db.JSON, nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<UserEvent "
            f"type={self.event_type} "
            f"object={self.object_type}:{self.object_id} "
            f"session={self.session_id}>"
        )
