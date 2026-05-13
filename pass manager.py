import json
import os
import random
import string
from getpass import getpass
import hashlib
from cryptography.fernet import Fernet
import logging
import shutil
from datetime import datetime
import pyperclip # for copy clip  board
import time
import tkinter as tk
from tkinter import messagebox,simpledialog
LOG_FILE = os.path.join(os.path.expanduser("~"), "activity.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
pass_login ="7ad040f26dd7b91f5367aec6ccbb579c0e8a6685f39a2982a35b7b6350f14fb2"

FILE = os.path.join(os.path.expanduser("~"), "password.json")

BACKUP_FOLDER = os.path.join(os.path.expanduser("~"), "pass_backups")
#hash pass

def verify_master():
    attempts = 3

    while attempts > 0:
        user = getpass("Enter master password: ")
        user_hash = hashlib.sha256(user.encode()).hexdigest()

        if user_hash == pass_login:
            print("Access granted.\n")
            logging.info("succesful login ")
            return True
        else:
            attempts -= 1
            print(f"Access denied. Attempts left: {attempts}")
            logging.warning("failed login atempt")
    print("Too many failed attempts. Program locked.")
    logging.critical("Program locked after 3 failed attempts")
    return False

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
        with open(FILE, "rb") as f: #rb menas read binary
            encrypted_data = f.read()

        decrypted_data = cipher.decrypt(encrypted_data).decode()
        return json.loads(decrypted_data)

    except:
        print("Error: Could not decrypt file.")
        return {}
   
#save the pass

def save_pass(data):
    json_data = json.dumps(data)
    encrypted_data = cipher.encrypt(json_data.encode())

    with open(FILE, "wb") as f:# wb use for binary
        f.write(encrypted_data)

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

# get the password and copy to clip board

def get_pass():
    data = load_data()
    site = input("Website/App name: ").strip()

    if site in data:
        print(f"\nSite : {site}")
        print(f"Username: {data[site]['username']}")

        encrypted_pwd = data[site]['password']
        decrypted_pwd = cipher.decrypt(encrypted_pwd.encode()).decode()

        choice = input("\n1. Show password\n2. Copy to clipboard\nChoose: ")

        if choice == "1":
            print(f"Password: {decrypted_pwd}")
        elif choice == "2":
            pyperclip.copy(decrypted_pwd)
            print("Password copied to clipboard.")
            print("clipboard will clear in 30 secends")

            time.sleep(30)
            pyperclip.copy("")
            print("clipboard cleared")
        else:
            print("Invalid option.")

    else:
        print("Website not found.")


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




def create_backup():
    if not os.path.exists(FILE):
        print("No password file to backup.")
        return

    # Create backup folder if it doesn't exist
    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    # Create timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    backup_file = os.path.join(
        BACKUP_FOLDER,
        f"backup_{timestamp}.json"
    )

    shutil.copy(FILE, backup_file)

    print("Backup created successfully.")




def search_site():
    data = load_data()

    if not data:
        print("No saved passwords.")
        return

    keyword = input("Enter search keyword: ").strip().lower()

    results = []

    for site in data:
        if keyword in site.lower():
            results.append(site)

    if results:
        print("\nSearch results:")
        for site in results:
            print("-", site)
    else:
        print("No matching websites found.")

class PasswordGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Password Manager V3")
        self.root.geometry("500x400")

        tk.Label(self.root, text="Password Manager", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Add Password", command=add_pass_gui).pack(fill="x")
        tk.Button(self.root, text="Get Password", command=get_pass_gui).pack(fill="x")
        tk.Button(self.root, text="Show Sites", command=show_sites_gui).pack(fill="x")
        tk.Button(self.root, text="Delete Password", command=delete_pass_gui).pack(fill="x")
        tk.Button(self.root, text="Search", command=search_site_gui).pack(fill="x")
        tk.Button(self.root, text="Exit", command=self.root.destroy).pack(fill="x")

        self.root.mainloop()


def add_pass_gui():
    site = simpledialog.askstring("Website", "Enter website:")
    username = simpledialog.askstring("Username", "Enter username:")
    pwd = simpledialog.askstring("Password", "Enter password (blank = generate):")

    if not site or not username:
        messagebox.showerror("Error", "Missing fields")
        return

    if not pwd:
        pwd = gen_pass()

    encrypted_pwd = cipher.encrypt(pwd.encode()).decode()

    data = load_data()
    data[site] = {"username": username, "password": encrypted_pwd}
    save_pass(data)

    messagebox.showinfo("Success", "Password saved!")

def get_pass_gui():
    site = simpledialog.askstring("Get Password", "Enter website:")

    if not site:
        return

    data = load_data()

    if site not in data:
        messagebox.showerror("Error", "Website not found")
        return

    username = data[site]["username"]
    encrypted_pwd = data[site]["password"]
    password = cipher.decrypt(encrypted_pwd.encode()).decode()

    win = tk.Toplevel()
    win.title("Password Details")
    win.geometry("300x200")

    tk.Label(win, text=f"Site: {site}").pack()
    tk.Label(win, text=f"Username: {username}").pack()
    tk.Label(win, text=f"Password: {password}").pack()

    def copy_pwd():
        pyperclip.copy(password)
        messagebox.showinfo("Copied", "Password copied!")

    tk.Button(win, text="Copy Password", command=copy_pwd).pack(pady=10)
def show_sites_gui():
    data = load_data()

    win = tk.Toplevel()
    win.title("Saved Sites")
    win.geometry("300x400")

    if not data:
        tk.Label(win, text="No saved passwords").pack()
        return

    tk.Label(win, text="Saved Websites:", font=("Arial", 12)).pack(pady=5)

    listbox = tk.Listbox(win)
    listbox.pack(expand=True, fill="both")

    for site in data:
        listbox.insert(tk.END, site)

    def copy_site():
        selected = listbox.get(tk.ACTIVE)
        if selected:
            pyperclip.copy(selected)
            messagebox.showinfo("Copied", "Website copied!")

    tk.Button(win, text="Copy Selected Site", command=copy_site).pack(pady=5)

def delete_pass_gui():
    site = simpledialog.askstring("Delete", "Enter website to delete:")

    if not site:
        return

    data = load_data()

    if site in data:
        del data[site]
        save_pass(data)
        messagebox.showinfo("Deleted", "Password deleted")
    else:
        messagebox.showerror("Error", "Website not found")

def search_site_gui():
    keyword = simpledialog.askstring("Search", "Enter keyword:")

    if not keyword:
        return

    data = load_data()

    results = [s for s in data if keyword.lower() in s.lower()]

    if results:
        messagebox.showinfo("Results", "\n".join(results))
    else:
        messagebox.showinfo("Results", "No matches found")

def main():
    if not verify_master():
        return

    mode = input("Choose mode: 1) CLI  2) GUI : ")

    if mode == "2":
        PasswordGUI()
    else:
        while True:
            print("\n1. add password"
                  "\n2. get password"
                  "\n3. show all"
                  "\n4. delete"
                  "\n5. update"
                  "\n6. backup"
                  "\n7. search"
                  "\n8. exit")

            ch = input("choose: ")

            if ch == "1": add_pass()
            elif ch == "2": get_pass()
            elif ch == "3": show_sites()
            elif ch == "4": delete_pass()
            elif ch == "5": update_pass()
            elif ch == "6": create_backup()
            elif ch == "7": search_site()
            elif ch == "8": break



if __name__ == "__main__":
     main()