import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ecitizen-secret-key-2026")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/mini_ecitizen_db")
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file upload limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    