# =====================================================
# ML EVENTS ROUTES (FINAL - FULLY DYNAMIC ✅)
# =====================================================

from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.user_event import UserEvent

# event_bp = Blueprint("event_bp", __name__, url_prefix="/api")     # Optional prefix for all routes in this blueprint
event_bp = Blueprint("event_bp", __name__)                          # No prefix, so routes are exactly as defined below (e.g. /health, /events)        


# ------------------------------------------------
# Health
# ------------------------------------------------
@event_bp.get("/health")
def api_health():
    return jsonify({"status": "ml-events-service up"}), 200


# ------------------------------------------------
# Collect Events (NO VALIDATION BLOCKING 🚀)
# ------------------------------------------------
@event_bp.post("/events")
def collect_event():
    data = request.get_json() or {}

    # ✅ Minimal required validation only
    if not data.get("user_id"):
        return jsonify({"error": "user_id required"}), 400

    if not data.get("event_type"):
        return jsonify({"error": "event_type required"}), 400

    try:
        event = UserEvent(
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            event_type=data.get("event_type"),
            object_type=data.get("object_type"),
            object_id=str(data.get("object_id")) if data.get("object_id") else None,
            event_metadata=data.get("event_metadata"),
        )

        db.session.add(event)
        db.session.commit()

        current_app.logger.info(f"Event stored: {event.event_type}")

        return jsonify({
            "message": "event stored",
            "event_type": event.event_type
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Event insert failed: {str(e)}")

        return jsonify({
            "error": "failed to store event"
        }), 500