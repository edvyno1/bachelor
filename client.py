import argparse
import requests
from util import generate_code
from sys import exit
from getpass import getpass
import json
import os

API_URL= "192.168.1.228"
API_BASE=f"http://{API_URL}:5000"

def does_phone_exist(phone) -> bool:
    phone_json = {'phone' : phone}
    response = requests.post(f"{API_BASE}/get_phone", json=phone_json)
    if response.status_code != 200:
        return True
    return False

def register(args):
    print(args)
    username = input("Enter the username you wish to register with: ") #validate empty input
    password = getpass("Enter your password: ")
    retype_password = getpass("Retype your password: ")
    if not password == retype_password:
        print("Password mismatch, exiting")
        exit()
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
    requests.post(f"{API_BASE}/sendsms", json=sms_post_data)
    try:
        input_code = int(input(f"Code was sent to {number} for confirmation, please enter it: "))
    except ValueError:
        print("Input is not a code")
        input_code = 0
    for i in range(3):
            if not input_code == code:
                print(type(input_code))
                print(f"DEBUG: input_code: {input_code}")
                print(type(code))
                print(f"DEBUG: code: {code}")
                try:
                    input_code = int(input("Code was incorrect, please try again: "))
                except ValueError:
                    print("Input is not a code")
                    continue
            else:
                break
    
    if not input_code == code:
        print("Try limit exceeded, exiting")
        exit()
    register_post_data = {'username' : username, 'password' : password, 'phone' : number}
    response = requests.post(f"{API_BASE}/register", json=register_post_data)
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
        HOME = os.getenv("HOME")
        with open(f"{HOME}/.2fa", "w") as f:
            f.write(username + "\n")
            for i in range(10):
                f.write(str(generate_code()) + "\n")

def login():
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    login_post_data = {'username' : username, 'password' : password}
    response = requests.post(f"{API_BASE}/login", json=login_post_data)
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
        response = requests.post(f"{API_BASE}/update/username", json=user_json)
        print(f"Response from server = {response.content}")
    else:
        print("Canceling change")

    #TODO REWRITE .2fa file with new username as well

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
        response = requests.post(f"{API_BASE}/update/password", json=user_json)
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
    requests.post(f"{API_BASE}/sendsms", json=sms_post_data)
    try:
        input_code = int(input(f"Code was sent to {new_phone} for confirmation, please enter it: "))
    except ValueError:
        print("Input is not a code")
        input_code = 0
    for i in range(3):
            if not input_code == code:
                print(type(input_code))
                print(f"DEBUG: input_code: {input_code}")
                print(type(code))
                print(f"DEBUG: code: {code}")
                try:
                    input_code = int(input("Code was incorrect, please try again: "))
                except ValueError:
                    print("Input is not a code")
                    continue
            else:
                break


    backup_code = ''
    while backup_code.strip() == '':
        backup_code = input("Enter one of your backup codes: ")
    user_json['backup_code'] = backup_code
    user_json['new_phone'] = new_phone
    response = requests.post(f"{API_BASE}/update/phone", json=user_json)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    register_parser = subparsers.add_parser("register", help="register to 2fa service")

    reset_parser = subparsers.add_parser("account", help="update details for existing account")


    args = parser.parse_args()
    if args.command =="register":
        register(args)
    elif args.command == "account":
        account(args)
        
