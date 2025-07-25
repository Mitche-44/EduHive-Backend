from flask import Flask
from config import Config
from extensions import db, migrate, bcrypt, cors
from flask_jwt_extended import JWTManager
from resources import api_bp

jwt = JWTManager()



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)



    # from models import User, Product, CartItem, Order

    # Register blueprints here later
    # from resources.customers import customers_bp
    # app.register_blueprint(customers_bp, url_prefix="/api/customers")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
