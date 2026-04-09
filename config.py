import os

class Config:
    # Secret Key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sanker-mobiles-secret-key-12345'
    
    # Database configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mail configuration (Gmail OTP)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ramyasivakumar0703@gmail.com'
    MAIL_PASSWORD = 'lalc kmgd dtvb nlmh'
    MAIL_DEFAULT_SENDER = 'ramyasivakumar0703@gmail.com'
    
    # OTP Demo Mode (Set to False for real email sending)
    DEMO_MODE = False
    
    # Upload configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
