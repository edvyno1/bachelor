from .database import db
from flask_bcrypt import generate_password_hash, check_password_hash
from util import generate_code
from hashlib import sha512


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, unique=True, nullable=False)
    codes = db.relationship('RecoveryCodes', backref='owner')
    
    def __init__(self, username, password, phone, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username = username
        self.password = password
        self.phone = phone
        

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode("utf-8")

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def hash_codes(self):
        print(self.codes)
        
class RecoveryCodes(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    code1 = db.Column(db.String)
    code2 = db.Column(db.String)
    code3 = db.Column(db.String)
    code4 = db.Column(db.String)
    code5 = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        super(RecoveryCodes, self).__init__(**kwargs)
        self.code1 = generate_code()
        self.code2 = generate_code()
        self.code3 = generate_code()
        self.code4 = generate_code()
        self.code5 = generate_code()

    def hash_codes(self):
        self.code1 = sha512(self.code1.encode("utf-8")).hexdigest()
        self.code2 = sha512(self.code2.encode("utf-8")).hexdigest()
        self.code3 = sha512(self.code3.encode("utf-8")).hexdigest()
        self.code4 = sha512(self.code4.encode("utf-8")).hexdigest()
        self.code5 = sha512(self.code5.encode("utf-8")).hexdigest()
        
