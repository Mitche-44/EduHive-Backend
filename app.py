from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, bcrypt, cors
from flask_jwt_extended import JWTManager
from datetime import datetime
from decouple import config
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

jwt = JWTManager()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Use the Config class
    app.config.from_object(Config)
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register main API blueprint (if it exists)
    try:
        from resources import api_bp
        app.register_blueprint(api_bp, url_prefix="/api")
        print("✅ Main API blueprint registered successfully")
    except ImportError as e:
        print(f"⚠️ Warning: Main API blueprint not found: {e}")
    
    # Import and register M-Pesa blueprint (if it exists)
    try:
        print("🔍 Attempting to import M-Pesa blueprint...")
        print(f"📁 Current working directory: {os.getcwd()}")
        print(f"📂 Resources directory exists: {os.path.exists('resources')}")
        print(f"📄 mpesa_blueprint.py exists: {os.path.exists('resources/mpesa_blueprint.py')}")
        
        from resources.mpesa_blueprint import mpesa_bp
        app.register_blueprint(mpesa_bp, url_prefix="/api/mpesa")
        print("✅ M-Pesa blueprint registered successfully!")
    except ImportError as e:
        print(f"❌ Error importing M-Pesa blueprint: {e}")
        print(f"🔍 Python path: {sys.path}")
        
        # Try to import step by step for debugging
        try:
            import resources
            print("✅ Resources module imported")
        except ImportError as e2:
            print(f"❌ Cannot import resources module: {e2}")
            
        try:
            import resources.mpesa_blueprint
            print("✅ mpesa_blueprint module imported")
        except ImportError as e3:
            print(f"❌ Cannot import mpesa_blueprint: {e3}")
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'OK',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config('MPESA_ENVIRONMENT', default='sandbox'),
            'database': app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0] if app.config.get('SQLALCHEMY_DATABASE_URI') else 'Not configured'
        })
    
    # Root endpoint
    @app.route('/')
    def home():
        return jsonify({
            'message': 'Flask API Server with M-Pesa Integration',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': 'GET /health',
                'main_api': '/api/*',
                'mpesa_stk_push': 'POST /api/mpesa/stk-push',
                'mpesa_status': 'GET /api/mpesa/status/<checkout_request_id>',
                'mpesa_callback': 'POST /api/mpesa/callback',
                'mpesa_timeout': 'POST /api/mpesa/timeout',
                'mpesa_payments': 'GET /api/mpesa/payments'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    # Configuration from environment
    debug_mode = config('DEBUG', default=True, cast=bool)
    port = config('PORT', default=5000, cast=int)
    
    print(f"🚀 Starting Flask server on port {port}")
    print(f"💾 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"🔧 M-Pesa Environment: {config('MPESA_ENVIRONMENT', default='sandbox')}")
    print(f"🐛 Debug mode: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)