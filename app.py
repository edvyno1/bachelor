from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def get():
    return "works"

@app.route("/", methods=['POST'])
def post():
    str_data = request.get_data().decode("utf-8")
    data = str_data.split("&")
    username = data[0].split("=")[1]
    code = data[1].split("=")[1]
    print(f"{username}\n{code}\n")
# TODO
# SET UP DB
# SET UP REGISTER
# SET UP LOGIN
# TEST SEND CODE TO NUMBER

    return "post"
