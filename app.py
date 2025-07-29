# app.py or main.py
from flask import Flask
from config import Config
from extensions import db, migrate, bcrypt, cors, socketio  # ✅ import socketio from extensions
from flask_jwt_extended import JWTManager
from resources import api_bp

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

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    # Init socketio (important!)
    socketio.init_app(app)

    # Register socket events
    from socketio_events import register_socket_events
    register_socket_events(socketio)

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
