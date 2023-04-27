from .database import db
from flask_bcrypt import generate_password_hash, check_password_hash
import random

def generate_code():
    return random.randint(101000, 998999)

class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, unique=True, nullable=False)
    recovery1 = db.Column(db.Integer)
    recovery2 = db.Column(db.Integer)
    recovery3 = db.Column(db.Integer)
    recovery4 = db.Column(db.Integer)
    recovery5 = db.Column(db.Integer)
    
    def __init__(self, username, password, phone):
        self.username = username
        self.password = password
        self.phone = phone
        self.recovery1 = generate_code()
        self.recovery2 = generate_code()
        self.recovery3 = generate_code()
        self.recovery4 = generate_code()
        self.recovery5 = generate_code()
    
    def hash_password(self):
        self.password = generate_password_hash(self.password).decode("utf-8")

    def check_password(self, password):
        return check_password_hash(self.password, password)
