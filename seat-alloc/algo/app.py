# Main entry point for the backend server.
# Run this file to start the Flask application with the development/production environment.
import sys
import os

# Ensure UTF-8 output on Windows (emoji in log messages)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path to allow importing 'algo' package if running directly
# This ensures that 'from algo.main import app' works even if running 'python algo/app.py'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algo.main import app

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Seat Allocation System - Modular Backend")
    print("=" * 70)
    flask_env = os.getenv('FLASK_ENV', 'production')
    is_debug = flask_env != 'production'
    print(f"🔧 Environment: {flask_env}")
    print(f"🐛 Debug Mode: {is_debug}")
    print("=" * 70)
    
    app.run(
        debug=is_debug,
        port=5000,
        host='0.0.0.0'
    )