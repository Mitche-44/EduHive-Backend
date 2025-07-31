from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, bcrypt, cors, mail, socketio
from flask_jwt_extended import JWTManager
from resources import api_bp
from models import leaderboard, newsletter, subscription, testimonial
from resources.admin.testimonial_admin import admin_testimonial_bp
from resources.admin.subscriptions import admin_subscriptions_bp
from resources.admin.admin_leaderboard import admin_leaderboard_bp

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    socketio.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_testimonial_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_subscriptions_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_leaderboard_bp, url_prefix="/api/admin")

    @app.route("/")
    def index():
        return jsonify({"message": "EduHive API is running"}), 200

    return app