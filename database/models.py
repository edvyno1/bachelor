from .database import db
from flask_bcrypt import generate_password_hash, check_password_hash
from util import generate_code
from hashlib import sha512

class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, unique=True, nullable=False)
    recovery1 = db.Column(db.String)
    recovery2 = db.Column(db.String)
    recovery3 = db.Column(db.String)
    recovery4 = db.Column(db.String)
    recovery5 = db.Column(db.String)
    
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
    
    def hash_codes(self):
        self.recovery1 = sha512(self.recovery1.encode("utf-8")).hexdigest()
        self.recovery2 = sha512(self.recovery2.encode("utf-8")).hexdigest()
        self.recovery3 = sha512(self.recovery3.encode("utf-8")).hexdigest()
        self.recovery4 = sha512(self.recovery4.encode("utf-8")).hexdigest()
        self.recovery5 = sha512(self.recovery5.encode("utf-8")).hexdigest()
