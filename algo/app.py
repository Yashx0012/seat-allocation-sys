# Main entry point for the backend server.
# Run this file to start the Flask application with the development/production environment.
import sys
import os

# Add parent directory to path to allow importing 'algo' package if running directly
# This ensures that 'from algo.main import app' works even if running 'python algo/app.py'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algo.main import app

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Seat Allocation System - Modular Backend")
    print("=" * 70)
    print(f"🔧 Environment: {os.getenv('FLASK_ENV', 'production')}")
    print("=" * 70)
    
    app.run(
        debug=True,
        port=5000,
        host='0.0.0.0'
    )