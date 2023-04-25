import argparse
import requests
from random import randint
from sys import exit
from getpass import getpass

API_BASE="http://10.6.5.13:5000"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    register_parser = subparsers.add_parser("register", help="register to 2fa service")


    args = parser.parse_args()
    if args.command =="register":
        print(args)
        username = input("Enter the username you wish to register with: ")
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
            exit()
        print("correct! lets go!")
        code = randint(101000, 998999)
        sms_post_data = {"code": code, "phone" : number}
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
            print(f"Code expected: 200, received: {response.status_code}, check if URL and creds are correct")
        else:
            print(f"Creation successful for username: {username}, number : {number}")
