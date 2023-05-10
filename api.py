from flask import Flask, jsonify, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database.database import db
from database.models import User, RecoveryCodes
from gsm import send
from sqlalchemy import exc, select, update, delete
from hashlib import sha512
import logging
import asyncio

logging.basicConfig(filename="app.log", encoding="utf-8", level=logging.DEBUG)

app = Flask(__name__)
app.config["SECRET_KEY"] = "change it later"

limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)


@app.route("/")
def get():
    return "works"


@app.route("/sendsms", methods=["POST"])
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


@app.route("/", methods=["POST"])
@limiter.exempt
def send_sms_from_c():
    str_data = request.get_data().decode("utf-8")
    data = str_data.split("&")
    username = data[0].split("=")[1].strip()
    code = data[1].split("=")[1].strip()
    print(data)
    statement = select(User.phone).where(User.username == username)
    result = db.session.execute(statement)
    try:
        phone = result.scalars().all()[0]
    except IndexError:
        return Response(f"No user with name - {username} exists", status=401)
    try:
        send(phone, code)
        return Response("Code sent to phone number", status=200)
    except:
        return Response("Something went wrong", status=500)


@app.route("/register", methods=["POST"])
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

    recovery = RecoveryCodes(owner=user)
    db.session.add(recovery)
    db.session.commit()
    user_backup_codes_response = jsonify(
        {
            "rec1": recovery.code1,
            "rec2": recovery.code2,
            "rec3": recovery.code3,
            "rec4": recovery.code4,
            "rec5": recovery.code5,
        }
    )
    recovery.hash_codes()
    # print(user_backup_codes_response)
    # print(user.codes)
    # print(user.codes[0].code1)
    user_backup_codes_response.status = 200
    
    db.session.commit()
    # print("Post hashing")
    return user_backup_codes_response


@app.route("/get_phone", methods=["POST"])
def check_phone():
    body = request.get_json()
    phone_nr = body["phone"]
    exists = db.session.query(User.id).filter_by(phone=phone_nr).first() is not None
    if exists:
        return Response("Phone exists", status=200)
    else:
        return Response("No such phone found", status=400)


@app.route("/update/username", methods=["PUT"])
def update_username():
    body = request.get_json()
    id = body["user_id"]
    usrname = body["username"]
    try:
        statement = update(User).where(User.id == id).values(username=usrname)
        db.session.execute(statement)
        db.session.commit()
    except exc.IntegrityError:
        return Response("Username already exists", 401)
    except:
        return Response("Something went wrong", status=500)
    return Response("Updated successfuly", status=200)


@app.route("/update/password", methods=["PUT"])
def update_password():
    body = request.get_json()
    id = body["user_id"]
    passw = body["password"]
    usr = User("_", password=passw, phone="_")
    usr.hash_password()
    passw = usr.password
    try:
        statement = update(User).where(User.id == id).values(password=passw)
        db.session.execute(statement)
        db.session.commit()
    except:
        return Response("Something went wrong", status=500)
    return Response("Updated successfuly", status=200)


@app.route("/update/phone", methods=["PUT"])
@limiter.limit("2 per minute")
def update_phone():
    body = request.get_json()
    id = body["user_id"]
    back_code: str = body["backup_code"]
    new_phone = body["new_phone"]
    if back_code == "USED":
        return Response("No such code exists", status=400)

    does_code_exist_statement = select(User).where(User.id == id)
    print(does_code_exist_statement)
    result1 = db.session.execute(does_code_exist_statement)
    user: User = result1.scalars().all()[0]
    user_codes = user.codes[0]
    code_array = [
        user_codes.code1,
        user_codes.code2,
        user_codes.code3,
        user_codes.code4,
        user_codes.code5,
    ]
    # print(type(code_array))
    # print(code_array[0])
    # print(type(back_code))
    # print(sha512(back_code.encode("utf-8")).hexdigest())
    # print(f"comparing {type(code_array[0])} with {type(back_code)}")
    if not sha512(back_code.encode("utf-8")).hexdigest() in code_array:
        return Response("No such code exists", status=400)
    if sha512(back_code.encode("utf-8")).hexdigest() == user_codes.code1:
        statement = (
            update(User).where(User.id == id).values(phone=new_phone)
        )
        statement2 = (
            update(RecoveryCodes).where(RecoveryCodes.user_id == id).values(code1="USED")
        )
    elif sha512(back_code.encode("utf-8")).hexdigest() == user_codes.code2:
        statement = (
            update(User).where(User.id == id).values(phone=new_phone)
        )
        statement2 = (
            update(RecoveryCodes).where(RecoveryCodes.user_id == id).values(code2="USED")
        )
    elif sha512(back_code.encode("utf-8")).hexdigest() == user_codes.code3:
        statement = (
            update(User).where(User.id == id).values(phone=new_phone)
        )
        statement2 = (
            update(RecoveryCodes).where(RecoveryCodes.user_id == id).values(code3="USED")
        )
    elif sha512(back_code.encode("utf-8")).hexdigest() == user_codes.code4:
        statement = (
            update(User).where(User.id == id).values(phone=new_phone)
        )
        statement2 = (
            update(RecoveryCodes).where(RecoveryCodes.user_id == id).values(code4="USED")
        )
    elif sha512(back_code.encode("utf-8")).hexdigest() == user_codes.code5:
        statement = (
            update(User).where(User.id == id).values(phone=new_phone)
        )
        statement2 = (
            update(RecoveryCodes).where(RecoveryCodes.user_id == id).values(code5="USED")
        )
    try:
        db.session.execute(statement)
        db.session.execute(statement2)
        db.session.commit()
    except Exception as e:
        print(e)
        return Response("Something went wrong", status=500)
    return Response("Updated successfuly", status=200)

@app.route("/delete", methods=["DELETE"])
def delete_user():
    body = request.get_json()
    id = body["user_id"]
    try:
        statement = delete(User).where(User.id == id)
        db.session.execute(statement)
        db.session.commit()
    except Exception as e:
        print(e)
        return Response("Something went wrong", status=500)
    return Response("Deleted successfuly", status=200)

@app.route("/login", methods=["POST"])
def login():
    # print("WE ARE IN THE BUILDING")
    # print(request.get_json())
    body = request.get_json()
    # print("POST BODY EXPERIENCE")
    username = body["username"]
    password = body["password"]
    # print("body got\n")
    try:
        statement = select(User).where(User.username == username)
        # print("check db\n")
        result = db.session.execute(statement)
        user_array = result.scalars().all()
        # print(type(user_array))
        # print(user_array)
        if not user_array:
            return Response("Username or password is wrong", status=401)
        user: User = user_array[0]
        # print(type(user))
        # print(user)
        if not user.check_password(password):
            return Response("Username or password is wrong", status=401)
        login_response = jsonify({"user_id": user.id})
        login_response.status = 200
        return login_response
    except:
        return Response("Username or password is wrong", status=401)
