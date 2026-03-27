import os
import logging
from pathlib import Path

# Base directory (now isolated to the algo folder itself, instead of jumping out into the parent monorepo root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Production environment check
_IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

class Config:
    # Security
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Warn if using default secret in production
    if _IS_PRODUCTION and SECRET_KEY == 'dev-secret-key-change-in-prod':
        logging.warning("⚠️  CRITICAL: Using default SECRET_KEY in production! Set FLASK_SECRET_KEY.")
    
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
