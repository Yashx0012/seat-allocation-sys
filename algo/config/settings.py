import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    # Security
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Database
    DB_NAME = "demo.db"
    DB_PATH = BASE_DIR / DB_NAME
    
    # File Uploads
    FEEDBACK_FOLDER = BASE_DIR / "feedback_files"
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    
    # Logging
    LOG_FILE = BASE_DIR / "app.log"
    LOG_LEVEL = "INFO"

    @staticmethod
    def ensure_dirs():
        """Ensure required directories exist"""
        Config.FEEDBACK_FOLDER.mkdir(exist_ok=True)
