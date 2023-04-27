from flask import Flask, jsonify, request, Response
from database.database import db
from database.models import User
from gsm import send
import random
from sqlalchemy import exc, select

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "change it later"

db.init_app(app)

def generate_code():
    return random.randint(101000, 998999)
    

@app.route('/')
def get():
    return "works"

@app.route('/sendsms', methods=['POST'])
def send_sms_from_python():
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
    except exc.IntegrityError:
        return Response("Given username or phone number is already in use", status=400)
    except:
        return Response("Something went wrong", status=500)
    
    
    user_backup_codes_response = jsonify({"rec1" : user.recovery1, "rec2": user.recovery2, "rec3": user.recovery3, "rec4": user.recovery4, "rec5": user.recovery5})
    print(user_backup_codes_response)
    user_backup_codes_response.status = 200
    return user_backup_codes_response

@app.route('/', methods=['POST'])
def send_sms_from_c():
    str_data = request.get_data().decode("utf-8")
    data = str_data.split("&")
    username = data[0].split("=")[1]
    code = data[1].split("=")[1]
    print(data)
    statement = select(User.phone).where(User.username == username)
    result = db.session.execute(statement)
    phone = result.scalars().all()[0]
    send(phone, code)


    return "post"

def main():
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0")


if __name__ == '__main__':
    main()
    
    