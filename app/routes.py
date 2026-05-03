from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user_event import UserEvent

# ✅ NO PREFIX HERE
event_bp = Blueprint("event_bp", __name__)


# ------------------------------------------------
# HEALTH
# ------------------------------------------------
@event_bp.get("/health")
def api_health():
    return jsonify({"status": "ml-events-service up"}), 200


# ------------------------------------------------
# EVENTS API
# ------------------------------------------------
@event_bp.post("/events")
def collect_event():
    data = request.get_json() or {}

    # ---------------------------
    # VALIDATION
    # ---------------------------
    if not data.get("user_id"):
        return jsonify({"error": "user_id required"}), 400

    VALID_EVENTS = [
        "view_product",
        "add_to_cart",
        "cart_view",
        "checkout_started",
        "checkout_completed",
        "variant_selected",
        "order_cancelled",
        "order_view",
        "order_details_view"
    ]

    event_type = data.get("event_type")

    if event_type not in VALID_EVENTS:
        return jsonify({"error": f"Invalid event_type: {event_type}"}), 400

    # ---------------------------
    # SAVE EVENT
    # ---------------------------
    event = UserEvent(
        user_id=data["user_id"],
        session_id=data.get("session_id"),
        event_type=event_type,
        object_type=data.get("object_type", "product"),
        object_id=data.get("object_id"),
        event_metadata=data.get("event_metadata"),
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": "event stored",
        "event_type": event.event_type
    }), 201
