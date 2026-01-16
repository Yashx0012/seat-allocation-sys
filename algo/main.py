# Application factory and configuration.
# Initializes the Flask app, sets up middleware (CORS, logging), and registers API blueprints.
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from algo.config.settings import Config
from algo.database import ensure_demo_db, close_db

# Import Blueprints
from algo.api.blueprints.sessions import session_bp
from algo.api.blueprints.students import student_bp
from algo.api.blueprints.allocations import allocation_bp
from algo.api.blueprints.pdf import pdf_bp
from algo.api.blueprints.classrooms import classrooms_bp
from algo.api.blueprints.dashboard import dashboard_bp
from algo.api.blueprints.admin import auth_bp, admin_bp
from algo.api.blueprints.health import health_bp
from algo.api.blueprints.feedback import feedback_bp

def create_app(test_config=None):
    # Setup Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Initializing Modular Flask Application...")
    
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuration
    app.config.from_object(Config)
    if test_config:
        app.config.from_mapping(test_config)
        
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Database Setup
    with app.app_context():
        ensure_demo_db()
        
    @app.teardown_appcontext
    def teardown_db(exception):
        close_db(exception)
        
    # Register Blueprints
    app.register_blueprint(session_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(allocation_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(classrooms_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(feedback_bp)
    
    from algo.api.blueprints.plans import plans_bp
    app.register_blueprint(plans_bp)
    app.register_blueprint(health_bp)
    
    # Global Activity Tracking (Middleware)
    from algo.database.queries.user_queries import UserQueries
    
    @app.after_request
    def track_activity(response):
        if request.path.startswith('/static') or request.method == 'OPTIONS':
            return response
        
        # Use request.user_id if available (after token_required)
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return response
            
        try:
             UserQueries.track_activity(user_id, request.path)
        except Exception:
             pass # Fail silently
        
        return response

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8000)