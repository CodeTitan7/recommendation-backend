from flask import Blueprint, request, jsonify
from utils.jwt_helper import decode_jwt
from models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
def get_profile():
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

        # Get user profile
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "status": "success",
            "user": {
                "id": str(user._id),
                "username": user.username,
                "email": user.email,
                "preferences": user.preferences,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }), 200

    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/preferences', methods=['PUT'])
def update_preferences():
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

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        preferences = data.get('preferences')

        if not preferences or not isinstance(preferences, dict):
            return jsonify({"error": "Valid preferences object is required"}), 400

        # Update user preferences
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.update_preferences(preferences)

        return jsonify({
            "status": "success",
            "message": "Preferences updated successfully",
            "preferences": preferences
        }), 200

    except Exception as e:
        print(f"Preferences error: {e}")
        return jsonify({"error": "Internal server error"}), 500
