import argparse
import requests
from util import generate_code
from sys import exit
from getpass import getpass
import json
import os
from hashlib import sha512

API_BASE=f"https://auth-api.com"
HOME = os.getenv("HOME")

def does_phone_exist(phone) -> bool:
    phone_json = {'phone' : phone}
    response = requests.post(f"{API_BASE}/get_phone", json=phone_json, verify='generated/auth-api.com.pem')
    if response.status_code != 200:
        return True
    return False

def register(args):
    print(args)
    username = ''
    while username.strip() == '':
        username = input("Enter the username you wish to register with: ")
    password = ''
    while password.strip() == '':
        password = getpass("Enter your password: ")
    retype_password = ''
    while retype_password.strip() == '':
        retype_password = getpass("Retype your password: ")
    if not password == retype_password:
        print("Password mismatch, exiting")
        exit(1)
    number = ''
    while number.strip() == '':
        number = input("Enter the the phone number to which codes should be delivered: ")
    print(f"Username: {username}\nPhone number: {number}")
    answer = input("Is the data correct? [y/n]").lower()
    if answer not in ["yes", "ye","y"]:
        print("Did not receive confirmation, exiting")
        exit(1)
    print("correct! lets go!")
    code = generate_code()
    sms_post_data = {"code": code, "phone" : number}
    if(does_phone_exist(number)):
        print("Given phone number is already being used")
        exit(1)
    # check if status is 200 before checking this
    requests.post(f"{API_BASE}/sendsms", json=sms_post_data, verify='generated/auth-api.com.pem')
    input_code = input(f"Code was sent to {number} for confirmation, please enter it: ")
    for i in range(3):
            if not input_code == code:
                print(type(input_code))
                print(f"DEBUG: input_code: {input_code}")
                print(type(code))
                print(f"DEBUG: code: {code}")
                input_code = input("Code was incorrect, please try again: ")
            else:
                break
    
    if not input_code == code:
        print("Try limit exceeded, exiting")
        exit(1)
    register_post_data = {'username' : username, 'password' : password, 'phone' : number}
    response = requests.post(f"{API_BASE}/register", json=register_post_data, verify='generated/auth-api.com.pem')
    if response.status_code != 200:
        print(f"Code expected: 200, received: {response.status_code}, message from server: {response.content}")
    else:
        print(f"Creation successful for username: {username}, number : {number}\nHere are the backup codes that you can use to change your settings such as username, password or phone number:")
        codes : dict = json.loads(response.content.decode("utf-8"))
        print("================")
        for code in codes.values():
            print(code)
        print("================")
        print("!!!MAKE SURE TO WRITE THESE CODES DOWN AS THEY WILL ONLY BE SHOWN NOW AND NEVER AGAIN!!!")
        
        with open(f"{HOME}/.2fa", "w") as f:
            f.write(username)

def login():
    username = ''
    while username.strip() == '':
        username = input("Enter your username: ")
    password = ''
    while password.strip() == '':
        password = getpass("Enter your password: ")
    login_post_data = {'username' : username, 'password' : password}
    response = requests.post(f"{API_BASE}/login", json=login_post_data, verify='generated/auth-api.com.pem')
    if response.status_code != 200:
        print(f"Login failed, message from server: {response.content}")
        exit(1)
    return response.json()

def print_menu():
    menu_options = {
    1: 'Change username',
    2: 'Change password',
    3: 'Change phone number',
    4: 'Exit',
    }
    for key in menu_options.keys():
        print (key, '--', menu_options[key] )

def change_username(user_json):
    new_username = ''
    while new_username.strip() == '':
        new_username = input("Enter your new username: ")
    print(f"This will now be your new username: {new_username}")
    conf = ''
    possible_answers = ['y','n']
    while conf not in possible_answers:
        conf = input("Are you sure about this change? [y/n]")
    if conf == 'y':
        user_json['username'] = new_username
        response = requests.post(f"{API_BASE}/update/username", json=user_json, verify='generated/auth-api.com.pem')
        print(f"Response from server = {response.content}")
    else:
        print("Canceling change")
    with open(f"{HOME}/.2fa", "r") as f:
        lines = f.readlines()
    lines[0] = new_username
    with open(f"{HOME}/.2fa", "w") as f:
        f.writelines(lines)

def change_password(user_json):
    new_password = ''
    while new_password.strip() == '':
        new_password = getpass("Enter your new password: ")
    retype = ''
    while retype.strip() == '':
        retype = getpass("Retype your new password: ")
    if not new_password == retype:
        print("Passwords do not match")
        return
    conf = ''
    possible_answers = ['y','n']
    while conf not in possible_answers:
        conf = input("Are you sure about this change? [y/n]")
    if conf == 'y':
        user_json['password'] = new_password
        response = requests.post(f"{API_BASE}/update/password", json=user_json, verify='generated/auth-api.com.pem')
        print(f"Response from server = {response.content}")
    else:
        print("Canceling change")

def change_phone(user_json):
    new_phone = ''
    print("Warning!")
    print("In order to change your phone number, you have will have to input a backup code, that you were given during your registration")
    while new_phone.strip() == '':
        new_phone = input("Enter your new phone number: ")
    code = generate_code()
    sms_post_data = {"code": code, "phone" : new_phone}
    if(does_phone_exist(new_phone)):
        print("Given phone number is already being used")
        return
    # check if status is 200 before checking this
    requests.post(f"{API_BASE}/sendsms", json=sms_post_data, verify='generated/auth-api.com.pem')
    input_code = input(f"Code was sent to {new_phone} for confirmation, please enter it: ")
    for i in range(3):
            if not input_code == code:
                print(type(input_code))
                print(f"DEBUG: input_code: {input_code}")
                print(type(code))
                print(f"DEBUG: code: {code}")
                input_code = input("Code was incorrect, please try again: ")
            else:
                break


    backup_code : str = ''
    while backup_code.strip() == '':
        backup_code = input("Enter one of your backup codes: ")
    user_json['backup_code'] = backup_code
    user_json['new_phone'] = new_phone
    response = requests.post(f"{API_BASE}/update/phone", json=user_json, verify='generated/auth-api.com.pem')
    print(f"Response from server = {response.content}")



def account(args):    
    user_json = login()
    print(user_json)
    print(type(user_json))
    while(True):
        print_menu()
        option = ''
        try:
            option = int(input('[1-4]: '))
        except:
            print("Not a number...\n")
        if option == 1:
            change_username(user_json)
        elif option == 2:
            change_password(user_json)
        elif option == 3:
            change_phone(user_json)
        elif option == 4:
            exit(1)
        else:
            print("Pick a number between 1 and 4")

def generate():
    try:
        f = open(f"{HOME}/.2fa", "r")
    except:
        print(f"Unable to open file in {HOME}/.2fa")
    lines = f.readlines()
    f.close()
    print("Here are the emergency codes that you can use to log in with no internet connection")
    print("=====")
    with open(f"{HOME}/.2fa", "w") as f:
        f.writelines(lines[0])
        for i in range(10):
            code = generate_code()
            print(code)
            f.write(sha512(code.encode("utf-8")).hexdigest() + "\n")
    print("=====")
    print("WRITE THEM DOWN AS THE VALUES HELD IN ~/.2fa WILL BE HASHED")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    register_parser = subparsers.add_parser("register", help="register to 2fa service")

    reset_parser = subparsers.add_parser("account", help="update details for existing account")

    generator_parser = subparsers.add_parser("generate", help="generate local backup codes for emergency use")


    args = parser.parse_args()
    if args.command =="register":
        register(args)
    elif args.command == "account":
        account(args)
    elif args.command == "generate":
        generate()
        
