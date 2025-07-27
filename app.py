from flask import Flask
from config import Config
from extensions import db, migrate, bcrypt, cors, jwt
from resources import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    jwt.init_app(app)

    # Register JWT callback handlers (after init_app)
    from utils import auth  # this registers the token loaders


    # Register your API blueprint
    app.register_blueprint(api_bp, url_prefix="/api")

    return app