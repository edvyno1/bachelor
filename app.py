from flask import Flask, jsonify, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database.database import db
from database.models import User
from gsm import send
from sqlalchemy import exc, select, update
from waitress import serve
import logging
logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "change it later"

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

db.init_app(app)

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
    try:
        send(destination, code)
        return Response("Code sent to phone number", status=200)
    except:
        return Response("Something went wrong", status=500)

@app.route('/', methods=['POST'])
@limiter.exempt
def send_sms_from_c():
    str_data = request.get_data().decode("utf-8")
    data = str_data.split("&")
    username = data[0].split("=")[1].strip()
    code = data[1].split("=")[1].strip()
    print(data)
    statement = select(User.phone).where(User.username == username)
    result = db.session.execute(statement)
    phone = result.scalars().all()[0]
    try:
        send(phone, code)
        return Response("Code sent to phone number", status=200)
    except:
        return Response("Something went wrong", status=500)


@app.route('/register', methods=['POST'])
def register():
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

@app.route('/get_phone', methods=['POST'])
def check_phone():
    body = request.get_json()
    phone_nr = body['phone']
    exists = db.session.query(User.id).filter_by(phone=phone_nr).first() is not None
    if exists:
        return Response("Phone number already in use",status=400)
    else:
        return Response("Unused, good to go", status=200)

@app.route('/update/username', methods=['POST'])
def update_username():
    body = request.get_json()
    id = body['user_id']
    usrname = body['username']
    try:
        statement = (
            update(User)
            .where(User.id == id)
            .values(username = usrname)
        )
        db.session.execute(statement)
        db.session.commit()
    except exc.IntegrityError:
        return Response("Username already exists", 401)
    except:
        return Response("Something went wrong", status=500)
    return Response("Updated successfuly", status=200)


@app.route('/update/password', methods=['POST'])
def update_password():
    body = request.get_json()
    id = body['user_id']
    passw = body['password']
    usr = User("_",password=passw, phone="_")
    usr.hash_password()
    passw = usr.password
    try:
        statement = (
            update(User)
            .where(User.id == id)
            .values(password = passw)
        )
        db.session.execute(statement)
        db.session.commit()
    except:
        return Response("Something went wrong", status=500)
    return Response("Updated successfuly", status=200)


@app.route('/update/phone', methods=['POST'])
@limiter.limit("2 per minute")
def update_phone():
    body = request.get_json()
    id = body['user_id']
    back_code = int(body['backup_code'])
    new_phone = body['new_phone']
    if back_code == -1:
        return Response("No such code exists", status=400)

    does_code_exist_statement = (
        select(User)
        .where(User.id == id)
    )
    print(does_code_exist_statement)
    result1 = db.session.execute(does_code_exist_statement)
    user : User = result1.scalars().all()[0]
    code_array = [user.recovery1, user.recovery2,user.recovery3,user.recovery4,user.recovery5]
    print(type(code_array))
    print(code_array)
    print(type(back_code))
    print(back_code)
    print(f"comparing {type(code_array[0])} with {type(back_code)}")
    if not back_code in code_array:
        return Response("No such code exists", status=400)
    if back_code == user.recovery1:
        statement = update(User).where(User.id == id).values(recovery1 = -1, phone=new_phone)
    elif back_code == user.recovery2:
        statement = update(User).where(User.id == id).values(recovery2 = -1, phone=new_phone)
    elif back_code == user.recovery3:
        statement = update(User).where(User.id == id).values(recovery3 = -1, phone=new_phone)
    elif back_code == user.recovery4:
        statement = update(User).where(User.id == id).values(recovery4 = -1, phone=new_phone)
    elif back_code == user.recovery5:
        statement = update(User).where(User.id == id).values(recovery5 = -1, phone=new_phone) 
    try:
        db.session.execute(statement)
        db.session.commit()
    except:
        return Response("Something went wrong", status=500)
    return Response("Updated successfuly", status=200)


@app.route('/login', methods=['POST'])
def login():
    print("WE ARE IN THE BUILDING")
    print(request.get_json())
    body = request.get_json()
    print("POST BODY EXPERIENCE")
    username = body["username"]
    password = body["password"]
    print("body got\n")
    try:
        statement = select(User).where(User.username == username)
        print("check db\n")
        result = db.session.execute(statement)
        user_array = result.scalars().all()
        print(type(user_array))
        print(user_array)
        if not user_array:
            return Response("Username or password is wrong", status=401)
        user : User = user_array[0]
        print(type(user))
        print(user)
        if not user.check_password(password):
            return Response("Username or password is wrong", status=401)
        login_response = jsonify({"user_id" : user.id})
        login_response.status = 200
        return login_response
    except:
        return Response("Username or password is wrong", status=401)

def main():
    with app.app_context():
        db.create_all()
    serve(app, host="0.0.0.0", port=5000, url_scheme='https')


if __name__ == '__main__':
    main()
    
    