from flask import Flask, jsonify, request, Response
from database.database import db
from database.models import User
from gsm import send
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "change it later"

db.init_app(app)

@app.route('/')
def get():
    return "works"

@app.route('/sendsms', methods=['POST'])
def sms_via_gsm():
    body = request.get_json()
    print(body)
    destination = body["phone"]
    code = body["code"]
    print(destination)
    print(code)
    send(destination, code)
    return "sent!"


@app.route('/register', methods=['POST'])
def register():
    # request.get_data().decode("utf-8")
    body = request.get_json()
    user = User(**body)
    user.hash_password()
    print(user)
    try:
        db.session.add(user)
        db.session.commit()
    except:
        return Response("Something went wrong", status=500)
    return Response("Success", status=200)

@app.route('/', methods=['POST'])
def post():
    str_data = request.get_data().decode("utf-8")
    data = str_data.split("&")
    # username = data[0].split("=")[1]
    # code = data[1].split("=")[1]
    # print(f"{username}\n{code}\n")
    print(data)


    return "post"

def main():
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0")


if __name__ == '__main__':
    main()
    
    