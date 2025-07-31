from datetime import datetime, timezone
from config.database import get_db
from bson import ObjectId

class History:
    def __init__(self, user_id, recommendation_type, genre, items, query_params=None):
        self.user_id = ObjectId(user_id)
        self.recommendation_type = recommendation_type
        self.genre = genre
        self.items = items
        self.query_params = query_params or {}
        self.timestamp = datetime.now(timezone.utc)
        
    def save(self):
        db = get_db()
        history_data = {
            "user_id": self.user_id,
            "recommendation_type": self.recommendation_type,
            "genre": self.genre,
            "items": self.items,
            "query_params": self.query_params,
            "timestamp": self.timestamp
        }
        result = db.history.insert_one(history_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_history(user_id, limit=50, offset=0):
        db = get_db()
        try:
            history = list(db.history.find(
                {"user_id": ObjectId(user_id)}
            ).sort("timestamp", -1).skip(offset).limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for item in history:
                item["_id"] = str(item["_id"])
                item["user_id"] = str(item["user_id"])
                
            return history
        except:
            return []
    
    @staticmethod
    def get_user_stats(user_id):
        db = get_db()
        try:
            # Type statistics
            type_pipeline = [
                {"$match": {"user_id": ObjectId(user_id)}},
                {"$group": {
                    "_id": "$recommendation_type",
                    "count": {"$sum": 1},
                    "last_accessed": {"$max": "$timestamp"}
                }}
            ]
            type_stats = list(db.history.aggregate(type_pipeline))
            
            # Genre preferences - handle both string and array genres
            genre_pipeline = [
                {"$match": {"user_id": ObjectId(user_id)}},
                {"$unwind": "$genre"},
                {"$group": {
                    "_id": "$genre",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            genre_stats = list(db.history.aggregate(genre_pipeline))
            
            total_count = db.history.count_documents({"user_id": ObjectId(user_id)})
            
            return {
                "type_stats": type_stats,
                "genre_preferences": genre_stats,
                "total_recommendations": total_count
            }
        except:
            return {
                "type_stats": [],
                "genre_preferences": [],
                "total_recommendations": 0
            }