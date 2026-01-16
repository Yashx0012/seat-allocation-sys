import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
