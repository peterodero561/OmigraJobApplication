from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    profile_pic = db.Column(db.String(100), nullable=True)
    phone_no = db.Column(db.String(50), nullable=True)

    def __init__(self, username, email, password, id=None):
        self.username = username
        self.email = email
        self.id = id
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return{
            'id': self.id,
            'username':self.username,
            'email': self.email,
            'profile_pic': self.profile_pic,
            'phone_no': self.phone_no,
            'password': self.password
        }
