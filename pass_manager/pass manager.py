import json
import os
import random
import string
from getpass import getpass
import hashlib
from cryptography.fernet import Fernet

pass_login ="7ad040f26dd7b91f5367aec6ccbb579c0e8a6685f39a2982a35b7b6350f14fb2"

FILE = os.path.join(os.path.expanduser("~"), "password.json")


#hash pass

def verify_master():
    user = getpass("Enter master password: ")
    user_hash = hashlib.sha256(user.encode()).hexdigest()

    if user_hash != pass_login:
        print("Access denied.")
        return False
    return True

#load key
def load_key():
    with open("key.key", "rb") as f:
        return f.read()

key = load_key()
cipher = Fernet(key)


def load_data():
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return{}
    
#save the pass

def save_pass(data):
    with open(FILE,"w") as f:
        json.dump(data,f,indent=4)
    

def gen_pass(length=12):
    chars = string.ascii_letters + \
        string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars)
                for _ in range(length)   )


#add the pass


def add_pass():
    data = load_data()
    site = input("weebsite/app name: ").strip()
    username = input("username/email: ").strip()
    choice = input("1.enter pass"\
                   "\n 2. generate strong pass: ")
    if choice == "2":
        length = int(input("Enter password length: "))
        pwd = gen_pass(length)
    else:
        pwd =  getpass("enter pass")
    encrypted_pwd = cipher.encrypt(pwd.encode()).decode()
    strength = check_strength(pwd)
    print(f"Password strength: {strength}")

    if strength == "Weak":
        print(" Warning: This password is weak!")
    data[site] = {
        "username": username,
        "password": encrypted_pwd
}
    save_pass(data)
    print("saved succesfully") 

# get the password

def get_pass():
    data = load_data()
    site = input("website/App name: ").strip()

    if site in data:
        print(f"\nSite : {site}")
        print(f"Username: {data[site]['username']}")

        encrypted_pwd = data[site]['password']
        decrypted_pwd = cipher.decrypt(encrypted_pwd.encode()).decode()

        print(f"password : {decrypted_pwd}")
    else:
        print("not found")


#update or delet the password

def update_pass():
    data = load_data()
    site = input("Enter website/app name to update: ").strip()

    if site not in data:
        print("Website not found.")
        return

    print(f"\nEditing: {site}")
    print("Leave field empty to keep old value.\n")

    # Update username
    new_username = input("New username/email: ").strip()
    if new_username:
        data[site]["username"] = new_username

    # Update password
    new_pwd = getpass("New password: ").strip()
    if new_pwd:
        strength = check_strength(new_pwd)
        print(f"Password strength: {strength}")

        if strength == "Weak":
            print("Warning: This password is weak!")

        encrypted_pwd = cipher.encrypt(new_pwd.encode()).decode()
        data[site]["password"] = encrypted_pwd

    save_pass(data)
    print("Updated successfully.")


#show the pass

def show_sites():
    data = load_data()

    if not data:
        print("No saved passwords.")
        return

    print("\nSaved websites:")
    for site in data:
        print("-", site)

#delet pass

def delete_pass():
    data = load_data()
    site = input("Enter website to delete: ").strip()

    if site in data:
        del data[site]
        save_pass(data)
        print("Deleted successfully.")
    else:
        print("Website not found.")


def check_strength(password):
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()" for c in password)

    score = 0

    if length >= 8:
        score += 1
    if has_upper:
        score += 1
    if has_lower:
        score += 1
    if has_digit:
        score += 1
    if has_symbol:
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"





def main():
    if not verify_master():
        return
    while True:
        print("\n1. add password : " \
              "\n2.get a passowrd : "\
                "\n3.show all passowrd: "\
                "\n4.delet passowrd: "\
                "\n5.update password"
                    "\n6. exit")
        ch = input("choose: ")
        if ch == "1": add_pass()
        elif ch == "2": get_pass()
        elif ch == "3":  show_sites()
        elif ch == "4": delete_pass()
        elif ch == "5": update_pass()
        elif ch == "6": break


if __name__ == "__main__":
     main()