# System health and diagnostic endpoints.
# Simple reachability check to verify that the backend services are running.
from flask import Blueprint, jsonify
import time
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Simple diagnostic endpoint to verify backend reachability"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "environment": os.getenv('FLASK_ENV', 'development'),
        "message": "Backend is alive and reachable"
    }), 200
