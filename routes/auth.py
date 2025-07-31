from flask import Blueprint, request, jsonify
from models.user import User
from utils.jwt_helper import generate_jwt
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        preferences = data.get('preferences', {"genres": [], "types": []})
        
        # Validation
        if not username or not email or not password:
            return jsonify({"error": "Username, email, and password are required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters long"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        if not validate_password(password):
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        # Check if user already exists
        if User.find_by_email(email):
            return jsonify({"error": "Email already registered"}), 409
        
        if User.find_by_username(username):
            return jsonify({"error": "Username already taken"}), 409
        
        # Create new user
        user = User(username=username, email=email, password=password, preferences=preferences)
        user_id = user.save()
        
        # Generate JWT token
        token = generate_jwt(user_id, username, email)
        
        return jsonify({
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "preferences": preferences
            }
        }), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user by email
        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Update last login
        user.update_last_login()
        
        # Generate JWT token
        token = generate_jwt(user._id, user.username, user.email)
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user._id),
                "username": user.username,
                "email": user.email,
                "preferences": user.preferences,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500
