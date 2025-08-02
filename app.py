from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, bcrypt, cors, mail, socketio
from flask_jwt_extended import JWTManager
from resources import api_bp

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # CORS for REST API routes
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "https://edu-hive-frontend.vercel.app"
            ]
        }
    }, supports_credentials=True)

    # Socket.IO CORS: Allow frontend domains
    socketio.init_app(app, cors_allowed_origins=[
        "http://localhost:5173",
        "https://edu-hive-frontend.vercel.app"
    ])

    # Root health check
    @app.route("/")
    def index():
        return jsonify({"message": "EduHive API is running"}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
