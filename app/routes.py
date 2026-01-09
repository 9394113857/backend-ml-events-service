from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user_event import UserEvent

# ------------------------------------------------
# Blueprint
# ------------------------------------------------
event_bp = Blueprint("event_bp", __name__, url_prefix="/api")


# ------------------------------------------------
# Health check
# GET /api/health
# ------------------------------------------------
@event_bp.get("/health")
def api_health():
    return jsonify({"status": "ml-events-service up"}), 200


# ------------------------------------------------
# Collect user events
# POST /api/events
# ------------------------------------------------
@event_bp.post("/events")
def collect_event():
    data = request.get_json() or {}

    if "session_id" not in data or "event_type" not in data:
        return jsonify({
            "error": "session_id and event_type are required"
        }), 400

    event = UserEvent(
        user_id=data.get("user_id"),               # nullable
        session_id=data["session_id"],             # required
        event_type=data["event_type"],             # required
        object_type=data.get("object_type"),
        object_id=data.get("object_id"),
        event_metadata=data.get("event_metadata"), # JSON
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": "event stored",
        "event_type": event.event_type
    }), 201
