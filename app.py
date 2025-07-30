# app.py or main.py
from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, bcrypt, cors, mail, socketio

from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from resources import api_bp
from models import leaderboard
from models import newsletter
from models import subscription
from models import testimonial
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

    # Init socketio (important!)
    socketio.init_app(app)

    # Register socket events
    from socketio_events import register_socket_events
    register_socket_events(socketio)

    # from models import User, Product, CartItem, Order

    # Register blueprints here later
    # from resources.customers import customers_bp
    # app.register_blueprint(customers_bp, url_prefix="/api/customers")

    #  Add root route here
    @app.route("/")
    def index():
        return jsonify({"message": "EduHive API is running"}), 200


    return app


if __name__ == "__main__":
    app = create_app()

    socketio.run(app, debug=True, host="0.0.0.0", port=5000)

