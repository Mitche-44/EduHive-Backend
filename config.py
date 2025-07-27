import os
from decouple import config

class Config:
    # Basic Flask configuration
    SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = config(
        'DATABASE_URL', 
        default='sqlite:///eduhive.db'  # Default SQLite database
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access"]
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='jwt-secret-string-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = False  # or set to timedelta(hours=1) for expiration
    
    # M-Pesa Configuration
    MPESA_ENVIRONMENT = config('MPESA_ENVIRONMENT', default='sandbox')
    MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY', default='')
    MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET', default='')
    MPESA_PASSKEY = config('MPESA_PASSKEY', default='')
    MPESA_SHORTCODE = config('MPESA_SHORTCODE', default='174379')
    MPESA_CALLBACK_URL = config('MPESA_CALLBACK_URL', default='http://localhost:5000/api/mpesa/callback')
    MPESA_TIMEOUT_URL = config('MPESA_TIMEOUT_URL', default='http://localhost:5000/api/mpesa/timeout')
    
    # Other configurations
    DEBUG = config('DEBUG', default=True, cast=bool)
    PORT = config('PORT', default=5000, cast=int)
    FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
    
    # CORS settings
    CORS_ORIGINS = config('CORS_ORIGINS', default='*')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = config(
        'DEV_DATABASE_URL',
        default='sqlite:///eduhive_dev.db'
    )

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default=None)
    
    # In production, make sure these are set
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable must be set in production")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests

# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
