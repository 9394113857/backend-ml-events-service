from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user_event import UserEvent

# ------------------------------------------------
# Blueprint
# ------------------------------------------------
event_bp = Blueprint("event_bp", __name__, url_prefix="/api")


# ------------------------------------------------
# Health check
# ------------------------------------------------
@event_bp.get("/health")
def api_health():
    return jsonify({"status": "ml-events-service up"}), 200


# ------------------------------------------------
# Collect user events
# ------------------------------------------------
@event_bp.post("/events")
def collect_event():
    data = request.get_json() or {}

    # =====================================================
    # 🔴 CRITICAL VALIDATIONS (FINAL VERSION)
    # =====================================================

    # 1. user_id required
    if not data.get("user_id"):
        return jsonify({"error": "user_id required"}), 400

    # 2. event_type validation (UPDATED ✅)
    VALID_EVENTS = [
        "view_product",
        "add_to_cart",
        "checkout",
        "remove_from_cart",
        "order_cancelled"   # ✅ ADDED
    ]

    event_type = data.get("event_type")

    if event_type not in VALID_EVENTS:
        return jsonify({"error": f"Invalid event_type: {event_type}"}), 400

    # 3. object_type handling (SMART FIX ✅)
    object_type = data.get("object_type")

    # 👉 For ML events → must be product
    if event_type in ["view_product", "add_to_cart", "checkout"]:
        if object_type != "product":
            return jsonify({"error": "object_type must be 'product'"}), 400

    # 👉 For cancel → allow flexible (since no product_id sometimes)
    if event_type == "order_cancelled":
        if object_type not in ["product", None]:
            return jsonify({"error": "Invalid object_type"}), 400

    # =====================================================
    # CREATE EVENT
    # =====================================================
    event = UserEvent(
        user_id=data["user_id"],
        session_id=data.get("session_id"),
        event_type=event_type,
        object_type=object_type if object_type else "product",
        object_id=data.get("object_id"),
        event_metadata=data.get("event_metadata"),
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": "event stored",
        "event_type": event.event_type
    }), 201
