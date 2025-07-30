from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO



jwt = JWTManager()
blacklist = set()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()
mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")  # globally available
# socketio = SocketIO()
