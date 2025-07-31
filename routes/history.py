from flask import Blueprint, request, jsonify
from utils.jwt_helper import decode_jwt
from models.history import History

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
def get_history():
    try:
        # JWT Authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        try:
            user_data = decode_jwt(token)
            user_id = user_data.get("user_id")
        except Exception as e:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 items
        offset = int(request.args.get('offset', 0))

        # Get user history
        history = History.get_user_history(user_id, limit=limit, offset=offset)

        return jsonify({
            "status": "success",
            "history": history,
            "count": len(history),
            "limit": limit,
            "offset": offset
        }), 200

    except Exception as e:
        print(f"History error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@history_bp.route('/history/stats', methods=['GET'])
def get_history_stats():
    try:
        # JWT Authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        try:
            user_data = decode_jwt(token)
            user_id = user_data.get("user_id")
        except Exception as e:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Get user stats
        stats = History.get_user_stats(user_id)

        return jsonify({
            "status": "success",
            "stats": stats
        }), 200

    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({"error": "Internal server error"}), 500
