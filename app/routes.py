from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user_event import UserEvent

# -----------------------------------
# Blueprint
# -----------------------------------
event_bp = Blueprint("event_bp", __name__, url_prefix="/api")


# -----------------------------------
# Health check (optional but useful)
# -----------------------------------
@event_bp.get("/")
def health():
    return jsonify({"status": "ml-events-service up"}), 200


# -----------------------------------
# Collect user events (ML data)
# -----------------------------------
@event_bp.post("/events")
def collect_event():
    data = request.get_json()

    # Basic validation
    if not data or "session_id" not in data or "event_type" not in data:
        return jsonify({"error": "session_id and event_type are required"}), 400

    event = UserEvent(
        user_id=data.get("user_id"),                 # nullable (guest allowed)
        session_id=data["session_id"],               # required
        event_type=data["event_type"],               # view, click, add_to_cart
        object_type=data.get("object_type"),          # product, page, category
        object_id=data.get("object_id"),              # product_id or route
        event_metadata=data.get("metadata"),          # JSON payload
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"status": "event stored"}), 201
