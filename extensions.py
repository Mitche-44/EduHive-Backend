from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from flask_socketio import SocketIO
from flask_mail import Mail



jwt = JWTManager()
blacklist = set()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()

mail = Mail()

# socketio = SocketIO()
socketio = SocketIO(cors_allowed_origins="*") 
