from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = None
db = None

def init_db():
    global client, db
    
    MONGO_URI = os.getenv('MONGO_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'recommendation_system')
    
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable is required")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        
        # Test connection
        client.admin.command('ping')
        print(f"Connected to MongoDB database: {DATABASE_NAME}")
        
        # Create indexes for performance
        db.users.create_index("email", unique=True)
        db.users.create_index("username", unique=True)
        db.history.create_index([("user_id", 1), ("timestamp", -1)])
        
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e

def get_db():
    global db
    if db is None:
        init_db()
    return db