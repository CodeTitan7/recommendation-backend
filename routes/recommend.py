from flask import Blueprint, request, jsonify
import requests
import os
from dotenv import load_dotenv
from utils.jwt_helper import decode_jwt
from models.history import History

load_dotenv()

recommend_bp = Blueprint('recommend', __name__)

RECOMMENDER_ENDPOINTS = {
    "movie": os.getenv("MOVIE_RECOMMENDER_URL"),
    "book": os.getenv("BOOK_RECOMMENDER_URL"),
    "tv": os.getenv("TV_RECOMMENDER_URL")
}

RESPONSE_KEYS = {
    "movie": "movies",
    "book": "books",
    "tv": "shows"
}

@recommend_bp.route('/recommend/tvshowrec', methods=['POST'])
def recommend():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        rec_type = data.get('type')
        genre = data.get('genre')
        top_k = data.get('top_k', 10)

        if not rec_type or not genre:
            return jsonify({"error": "Missing 'type' or 'genre'"}), 400

        if rec_type not in RECOMMENDER_ENDPOINTS or not RECOMMENDER_ENDPOINTS[rec_type]:
            return jsonify({"error": "Invalid or missing recommender URL for type."}), 400

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

        # Process genres
        genres_list = [g.strip() for g in genre.split(",")] if isinstance(genre, str) else genre

        # Call microservice
        try:
            recommender_url = RECOMMENDER_ENDPOINTS[rec_type]
            response = requests.post(
                recommender_url,
                json={"genres": genres_list},
                timeout=10
            )

            if not response.ok:
                return jsonify({
                    "error": f"{rec_type} service error", 
                    "details": response.text,
                    "status_code": response.status_code
                }), 500

            result = response.json()
            if result.get("status") != "success":
                return jsonify({"error": result.get("message", "Unknown error")}), 500

            raw_items = result.get(RESPONSE_KEYS.get(rec_type, "items"), [])

            # Normalize response format
            normalized = []
            for item in raw_items:
                normalized.append({
                    "type": rec_type,
                    "name": item.get("name") or item.get("title"),  
                    "creator": item.get("director") or item.get("author") or item.get("creator"),
                    "description": item.get("description", ""),
                    "genre": item.get("genre", []),
                    "rating": item.get("rating"),
                    "year": item.get("year"),
                    "image_url": item.get("image_url")
                })

            # Save to history
            try:
                history = History(
                    user_id=user_id,
                    recommendation_type=rec_type,
                    genre=genres_list,
                    items=normalized,
                    query_params={"top_k": top_k}
                )
                history.save()
                print(f"Saved recommendation history for user {user_id}")
            except Exception as e:
                print(f"Failed to save history: {e}")
                # Don't fail the request if history saving fails

            return jsonify({
                "status": "success",
                "recommendations": normalized,
                "count": len(normalized),
                "type": rec_type,
                "genres": genres_list
            }), 200

        except requests.exceptions.Timeout:
            return jsonify({"error": f"{rec_type} service timeout"}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to connect to {rec_type} service", "details": str(e)}), 503

    except Exception as e:
        print(f"Recommend error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@recommend_bp.route('/recommend/movies', methods=['POST'])
def recommend():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        rec_type = data.get('type')
        genre = data.get('genre')
        top_k = data.get('top_k', 10)

        if not rec_type or not genre:
            return jsonify({"error": "Missing 'type' or 'genre'"}), 400

        if rec_type not in RECOMMENDER_ENDPOINTS or not RECOMMENDER_ENDPOINTS[rec_type]:
            return jsonify({"error": "Invalid or missing recommender URL for type."}), 400

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

        # Process genres
        genres_list = [g.strip() for g in genre.split(",")] if isinstance(genre, str) else genre

        # Call microservice
        try:
            recommender_url = RECOMMENDER_ENDPOINTS[rec_type]
            response = requests.post(
                recommender_url,
                json={"genres": genres_list, "top_k": top_k},
                timeout=10
            )

            if not response.ok:
                return jsonify({
                    "error": f"{rec_type} service error", 
                    "details": response.text,
                    "status_code": response.status_code
                }), 500

            result = response.json()
            if result.get("status") != "success":
                return jsonify({"error": result.get("message", "Unknown error")}), 500

            raw_items = result.get(RESPONSE_KEYS.get(rec_type, "items"), [])

            # Normalize response format
            normalized = []
            for item in raw_items:
                normalized.append({
                    "type": rec_type,
                    "name": item.get("name") or item.get("title"),  
                    "creator": item.get("director") or item.get("author") or item.get("creator"),
                    "description": item.get("description", ""),
                    "genre": item.get("genre", []),
                    "rating": item.get("rating")
                })

            # Save to history
            try:
                history = History(
                    user_id=user_id,
                    recommendation_type=rec_type,
                    genre=genres_list,
                    items=normalized,
                    query_params={"top_k": top_k}
                )
                history.save()
                print(f"Saved recommendation history for user {user_id}")
            except Exception as e:
                print(f"Failed to save history: {e}")
                # Don't fail the request if history saving fails

            return jsonify({
                "status": "success",
                "recommendations": normalized,
                "count": len(normalized),
                "type": rec_type,
                "genres": genres_list
            }), 200

        except requests.exceptions.Timeout:
            return jsonify({"error": f"{rec_type} service timeout"}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to connect to {rec_type} service", "details": str(e)}), 503

    except Exception as e:
        print(f"Recommend error: {e}")
        return jsonify({"error": "Internal server error"}), 500
