from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from config.database import get_db
from bson import ObjectId

class User:
    def __init__(self, username=None, email=None, password=None, preferences=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.preferences = preferences or {"genres": [], "types": []}
        self.created_at = datetime.now(timezone.utc)
        self.last_login = None
        
    def save(self):
        db = get_db()
        user_data = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "preferences": self.preferences,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
        result = db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_email(email):
        db = get_db()
        user_data = db.users.find_one({"email": email})
        if user_data:
            user = User()
            user._id = user_data["_id"]
            user.username = user_data["username"]
            user.email = user_data["email"]
            user.password_hash = user_data["password_hash"]
            user.preferences = user_data.get("preferences", {"genres": [], "types": []})
            user.created_at = user_data["created_at"]
            user.last_login = user_data.get("last_login")
            return user
        return None
    
    @staticmethod
    def find_by_username(username):
        db = get_db()
        user_data = db.users.find_one({"username": username})
        if user_data:
            user = User()
            user._id = user_data["_id"]
            user.username = user_data["username"]
            user.email = user_data["email"]
            user.password_hash = user_data["password_hash"]
            user.preferences = user_data.get("preferences", {"genres": [], "types": []})
            user.created_at = user_data["created_at"]
            user.last_login = user_data.get("last_login")
            return user
        return None
    
    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        try:
            user_data = db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                user = User()
                user._id = user_data["_id"]
                user.username = user_data["username"]
                user.email = user_data["email"]
                user.password_hash = user_data["password_hash"]
                user.preferences = user_data.get("preferences", {"genres": [], "types": []})
                user.created_at = user_data["created_at"]
                user.last_login = user_data.get("last_login")
                return user
        except:
            pass
        return None
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        db = get_db()
        self.last_login = datetime.now(timezone.utc)
        db.users.update_one(
            {"_id": self._id},
            {"$set": {"last_login": self.last_login}}
        )
    
    def update_preferences(self, preferences):
        db = get_db()
        self.preferences = preferences
        db.users.update_one(
            {"_id": self._id},
            {"$set": {"preferences": preferences}}
        )
