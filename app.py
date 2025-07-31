from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, bcrypt, cors, mail, socketio
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from resources import api_bp





jwt = JWTManager()



def create_app():
    app = Flask(__name__)

    # Use the Config class
    app.config.from_object(Config)
    jwt.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    socketio.init_app(app)



    # from models import User, Product, CartItem, Order

    # Register blueprints here later
    # from resources.customers import customers_bp
    # app.register_blueprint(customers_bp, url_prefix="/api/customers")

    # ✅ Add root route here

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


