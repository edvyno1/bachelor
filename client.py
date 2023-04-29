import argparse
import requests
from util import generate_code
from sys import exit
from getpass import getpass
import json
import os

API_URL= "192.168.1.228"
API_BASE=f"http://{API_URL}:5000"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    register_parser = subparsers.add_parser("register", help="register to 2fa service")


    args = parser.parse_args()
    if args.command =="register":
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
            exit()
        print("correct! lets go!")
        code = generate_code()
        sms_post_data = {"code": code, "phone" : number}
        # CHECK IF NUMBER ALREADY EXISTS BEFORE WE SEND SMS!!!!!!!!!!!!!
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
