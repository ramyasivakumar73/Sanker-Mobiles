from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True) # Optional for initial admin
    phone = db.Column(db.String(20), unique=True, nullable=True) # Optional for initial admin
    password_hash = db.Column(db.String(128))
    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0) # Percentage
    fixed_discount = db.Column(db.Float, default=0) # Flat amount
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    material = db.Column(db.String(100))
    size = db.Column(db.String(50))
    color = db.Column(db.String(50))
    shape = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    quality = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)
    warranty = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
