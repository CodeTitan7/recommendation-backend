from flask import Flask
from flask_cors import CORS
from config.database import init_db
from routes.auth import auth_bp
from routes.recommend import recommend_bp
from routes.history import history_bp
from routes.user import user_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Enable CORS
CORS(app)

# Initialize MongoDB
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(recommend_bp)
app.register_blueprint(history_bp)
app.register_blueprint(user_bp, url_prefix='/user')

@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy", "message": "Flask backend is running"}, 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)