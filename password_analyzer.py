import tkinter as tk
from tkinter.ttk import Progressbar, Treeview
import re
import hashlib
import os
import csv

# -------------------------------
# Global Variables
# -------------------------------
saved_passwords = []  # List of tuples: (username, password, encrypted)
logged_in = False     # Flag to indicate whether the user has successfully logged in
settings_message = None  # Reference for temporary messages in the Settings view

# -------------------------------
# Load Icon Images
# -------------------------------
# Ensure that 'change_icon.png' and 'delete_icon.png' are available in the working directory.
try:
    change_icon = tk.PhotoImage(file="change_icon.png")
    delete_icon = tk.PhotoImage(file="delete_icon.png")
except Exception as e:
    print("Error loading icon images:", e)
    change_icon = None
    delete_icon = None

# -------------------------------
# Utility Functions and Data Loading
# -------------------------------
def load_weak_passwords():
    """
    Load a set of weak/common passwords from a file.
    If the file is not found, a default set is returned.
    """
    try:
        with open("weak_passwords.txt", "r") as file:
            return set(line.strip().lower() for line in file)
    except FileNotFoundError:
        return {"password", "123456", "qwerty", "admin", "letmein", "welcome"}

WEAK_PASSWORDS = load_weak_passwords()

# Passphrase file utilities for persistent settings.
def load_passphrase():
    """
    Load the passphrase from 'passphrase.txt' if it exists.
    """
    if os.path.exists("passphrase.txt"):
        with open("passphrase.txt", "r") as f:
            return f.read().strip()
    return None

def save_passphrase_to_file(pp):
    """
    Save the passphrase to 'passphrase.txt'.
    """
    with open("passphrase.txt", "w") as f:
        f.write(pp)

def delete_passphrase_file():
    """
    Delete the 'passphrase.txt' file.
    """
    if os.path.exists("passphrase.txt"):
        os.remove("passphrase.txt")

# Load passphrase on startup.
passphrase = load_passphrase()

def load_passwords_from_csv():
    """
    Load saved passwords from 'saved_passwords.csv' into the saved_passwords list.
    CSV format: Username, Password, Encrypted.
    """
    global saved_passwords
    if os.path.exists("saved_passwords.csv"):
        with open("saved_passwords.csv", "r", newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # Skip header row
            for row in reader:
                if len(row) >= 3:
                    username, password, encrypted = row[0], row[1], row[2]
                    saved_passwords.append((username, password, encrypted))

# -------------------------------
# Utility: Temporary Message Display
# -------------------------------
def show_temporary_message(label, message, fg="green", duration=3000):
    """
    Display a temporary message in the provided label.
    The message clears after 'duration' milliseconds.
    """
    label.config(text=message, fg=fg)
    label.after(duration, lambda: label.config(text=""))

# -------------------------------
# Password-Related Functions
# -------------------------------
def encrypt_password(password, salt=""):
    """
    Encrypt the given password using SHA-256 with the provided salt (passphrase).
    """
    return hashlib.sha256((password + salt).encode()).hexdigest()

def analyze_password(password, username=""):
    """
    Analyze the password strength and return:
      - Strength level ("Weak", "Moderate", "Strong")
      - Score
      - Suggestions for improvement
      - Any warnings (e.g. if the password contains the username)
    """
    if not password:
        return "", 0, [], ""
    
    if username and username.lower() in password.lower():
        return "Weak", 0, ["Avoid using your username in the password."], "⚠ Password contains username!"
    
    if password.lower() in WEAK_PASSWORDS:
        return "Weak", 0, ["This password is too common!"], ""
    
    score = 0
    suggestions = []
    warning = ""
    
    # Check length
    if len(password) >= 12:
        score += 3
    elif len(password) >= 8:
        score += 2
    else:
        suggestions.append("Use at least 8 characters.")
    
    # Check for uppercase and lowercase letters
    if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password):
        score += 2
    else:
        suggestions.append("Mix uppercase and lowercase letters.")
    
    # Check for digits
    if re.search(r'\d', password):
        score += 2
    else:
        suggestions.append("Include at least one number.")
    
    # Check for special characters
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 2
    else:
        suggestions.append("Use at least one special character.")
    
    if score <= 2:
        return "Weak", score, suggestions, warning
    elif score <= 6:
        return "Moderate", score, suggestions, warning
    else:
        return "Strong", score, suggestions, warning

def on_key_release(event):
    """
    Callback for updating password strength as the user types.
    """
    password = password_entry.get()
    username = username_entry.get()
    strength, score, suggestions, warning = analyze_password(password, username)
    progress_bar["value"] = max((score / 10) * 100, 5)
    strength_label.config(
        text=f"Strength: {strength}",
        fg=("red" if strength == "Weak" else "orange" if strength == "Moderate" else "green")
    )
    suggestions_label.config(text="\n".join(suggestions) if strength == "Weak" else "")
    warning_label.config(text=warning if warning else "")

def save_password():
    """
    Save the password entered in the Analyzer view.
    The password is encrypted with the passphrase as salt.
    """
    global passphrase
    if passphrase is None:
        save_message.config(text="⚠ Set a passphrase in Settings!", fg="red")
        return

    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        hashed = encrypt_password(password, passphrase)
        saved_passwords.append((username, password, hashed))
        # Insert masked password into the manager view
        password_list.insert("", "end", values=(username, "********"))
        save_message.config(text="✅ Password successfully saved!", fg="green")
        save_passwords_to_csv()

def save_passwords_to_csv():
    """
    Save all password entries to a CSV file.
    """
    global passphrase
    if passphrase is None:
        return
    with open("saved_passwords.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Username", "Password", "Encrypted"])
        for username, password, encrypted in saved_passwords:
            writer.writerow([username, password, encrypted])

# -------------------------------
# Manager UI Functions
# -------------------------------
def populate_manager_view():
    """
    Populate the manager Treeview with saved password entries.
    """
    password_list.delete(*password_list.get_children())
    for username, password, _ in saved_passwords:
        password_list.insert("", "end", values=(username, password))

def manager_view_login():
    """
    Validate the passphrase entered in the Manager view.
    If correct, display all saved passwords.
    """
    global logged_in, passphrase
    entered = manager_pass_entry.get()
    if entered == passphrase:
        logged_in = True
        populate_manager_view()
        login_message.config(text="✅ Logged in. Passwords revealed!", fg="green")
        manager_login_frame.pack_forget()
    else:
        login_message.config(text="❌ Incorrect passphrase!", fg="red")

def show_manager():
    """
    Switch to the Manager view.
    If not logged in, display the login controls centered at the bottom.
    """
    global logged_in
    analyzer_frame.pack_forget()
    settings_frame.pack_forget()
    manager_frame.pack(fill="both", expand=True)
    password_list.delete(*password_list.get_children())
    if not logged_in:
        # Center the login frame (entry and button side by side) at the bottom.
        manager_login_frame.pack(side="bottom", pady=10, anchor="center")
        login_message.pack(side="bottom", pady=5, anchor="center")
        login_message.config(text="Enter passphrase to view saved passwords.", fg="blue")
    else:
        populate_manager_view()

# -------------------------------
# Settings UI Functions
# -------------------------------
def setup_passphrase(entry_widget):
    """
    Set a new passphrase from the given entry widget.
    Save the passphrase to file and refresh the Settings view.
    """
    global passphrase, settings_message
    entered = entry_widget.get()
    if entered:
        passphrase = entered
        save_passphrase_to_file(passphrase)
        show_temporary_message(settings_message, "✅ Passphrase set successfully!", "green")
        refresh_settings_frame()
    else:
        show_temporary_message(settings_message, "⚠ Passphrase cannot be empty!", "red")

def refresh_settings_frame():
    """
    Refresh the Settings view.
    If no passphrase is set, display the controls to set one.
    If a passphrase exists, display a horizontal bar with the guest name and action icons.
    """
    global settings_message
    for widget in settings_frame.winfo_children():
        widget.destroy()
    if passphrase is None:
        # Show new passphrase input controls.
        p_label = tk.Label(settings_frame, text="Set a Passphrase:", font=("Arial", 12))
        p_label.pack(pady=5)
        p_entry = tk.Entry(settings_frame, show="*", font=("Arial", 10))
        p_entry.pack(pady=5)
        set_btn = tk.Button(settings_frame, text="Set Passphrase", command=lambda: setup_passphrase(p_entry))
        set_btn.pack(pady=10)
        settings_message = tk.Label(settings_frame, text="", font=("Arial", 10))
        settings_message.pack(pady=5)
    else:
        # Show horizontal bar with guest name on left and icon buttons on right.
        horizontal_bar = tk.Frame(settings_frame)
        horizontal_bar.pack(fill="x", pady=5, padx=5)
        guest_label = tk.Label(horizontal_bar, text="Guest1", font=("Arial", 12))
        guest_label.pack(side="left")
        icons_frame = tk.Frame(horizontal_bar)
        icons_frame.pack(side="right")
        if change_icon:
            change_btn = tk.Button(icons_frame, image=change_icon, command=show_change_passphrase_ui, borderwidth=0, highlightthickness=0)
        else:
            change_btn = tk.Button(icons_frame, text="Change", command=show_change_passphrase_ui)
        change_btn.pack(side="left", padx=5)
        if delete_icon:
            delete_btn = tk.Button(icons_frame, image=delete_icon, command=delete_account, borderwidth=0, highlightthickness=0)
        else:
            delete_btn = tk.Button(icons_frame, text="Delete", command=delete_account)
        delete_btn.pack(side="left", padx=5)
        settings_message = tk.Label(settings_frame, text="", font=("Arial", 10))
        settings_message.pack(pady=5)
    settings_frame.settings_message = settings_message

def show_change_passphrase_ui():
    """
    Switch the Settings view to the change passphrase interface.
    """
    for widget in settings_frame.winfo_children():
        widget.destroy()
    old_label = tk.Label(settings_frame, text="Enter current Passphrase:", font=("Arial", 12))
    old_label.pack(pady=5)
    old_entry = tk.Entry(settings_frame, show="*", font=("Arial", 10))
    old_entry.pack(pady=5)
    new_label = tk.Label(settings_frame, text="Enter new Passphrase:", font=("Arial", 12))
    new_label.pack(pady=5)
    new_entry = tk.Entry(settings_frame, show="*", font=("Arial", 10))
    new_entry.pack(pady=5)
    confirm_label = tk.Label(settings_frame, text="Confirm new Passphrase:", font=("Arial", 12))
    confirm_label.pack(pady=5)
    confirm_entry = tk.Entry(settings_frame, show="*", font=("Arial", 10))
    confirm_entry.pack(pady=5)
    msg_label = tk.Label(settings_frame, text="", font=("Arial", 10))
    msg_label.pack(pady=5)
    submit_btn = tk.Button(settings_frame, text="Change Passphrase", 
                           command=lambda: change_passphrase(old_entry, new_entry, confirm_entry, msg_label))
    submit_btn.pack(pady=5)
    back_btn = tk.Button(settings_frame, text="Back", command=refresh_settings_frame)
    back_btn.pack(pady=5)

def change_passphrase(old_entry, new_entry, confirm_entry, msg_label):
    """
    Validate and change the passphrase.
    """
    global passphrase
    old = old_entry.get()
    new = new_entry.get()
    confirm = confirm_entry.get()
    if old != passphrase:
        msg_label.config(text="Incorrect current passphrase!", fg="red")
        return
    if new != confirm:
        msg_label.config(text="New passphrase and confirmation do not match!", fg="red")
        return
    if not new:
        msg_label.config(text="New passphrase cannot be empty!", fg="red")
        return
    passphrase = new
    save_passphrase_to_file(passphrase)
    show_temporary_message(msg_label, "✅ Passphrase changed successfully!", "green")
    refresh_settings_frame()

def delete_account():
    """
    Delete the account by removing the passphrase and all saved passwords.
    """
    global passphrase, saved_passwords, logged_in
    passphrase = None
    logged_in = False
    delete_passphrase_file()
    saved_passwords = []
    if os.path.exists("saved_passwords.csv"):
        os.remove("saved_passwords.csv")
    refresh_settings_frame()

def show_settings():
    """
    Switch to the Settings view.
    """
    analyzer_frame.pack_forget()
    manager_frame.pack_forget()
    settings_frame.pack(fill="both", expand=True)
    refresh_settings_frame()

# -------------------------------
# Navigation Functions
# -------------------------------
def show_analyzer():
    """
    Switch to the Analyzer view.
    """
    manager_frame.pack_forget()
    settings_frame.pack_forget()
    analyzer_frame.pack(fill="both", expand=True)

# -------------------------------
# GUI Setup
# -------------------------------
root = tk.Tk()
root.title("SecurePass Manager")
root.geometry("500x500")
root.resizable(False, False)

# Navigation Bar
navbar = tk.Frame(root, bg="#333", height=40)
navbar.pack(fill="x")
analyzer_btn = tk.Button(navbar, text="Analyzer", bg="#444", fg="white", borderwidth=0, command=show_analyzer)
analyzer_btn.pack(side="left", padx=10, pady=5)
manager_btn = tk.Button(navbar, text="Manager", bg="#444", fg="white", borderwidth=0, command=show_manager)
manager_btn.pack(side="left", padx=10, pady=5)
settings_btn = tk.Button(navbar, text="⚙", bg="#333", fg="white", borderwidth=0,
                         font=("Arial", 12, "bold"), command=show_settings)
settings_btn.pack(side="right", padx=10, pady=5)

# -------------------------------
# Analyzer Frame Setup
# -------------------------------
analyzer_frame = tk.Frame(root)
username_label = tk.Label(analyzer_frame, text="Enter username (optional):", font=("Arial", 10))
username_label.pack(pady=5)
username_entry = tk.Entry(analyzer_frame, font=("Arial", 10))
username_entry.pack(pady=2)
password_label = tk.Label(analyzer_frame, text="Enter password:", font=("Arial", 12))
password_label.pack(pady=10)
password_entry = tk.Entry(analyzer_frame, show="*", font=("Arial", 12))
password_entry.pack(pady=5)
password_entry.bind("<KeyRelease>", on_key_release)
progress_bar = Progressbar(analyzer_frame, length=300, mode="determinate")
progress_bar.pack(pady=10)
strength_label = tk.Label(analyzer_frame, text="Strength: ", font=("Arial", 12, "bold"))
strength_label.pack()
suggestions_label = tk.Label(analyzer_frame, text="", font=("Arial", 10), fg="red")
suggestions_label.pack(pady=5)
warning_label = tk.Label(analyzer_frame, text="", font=("Arial", 10), fg="red")
warning_label.pack(pady=5)
save_button = tk.Button(analyzer_frame, text="Save Password", command=save_password)
save_button.pack(pady=10)
save_message = tk.Label(analyzer_frame, text="", font=("Arial", 10), fg="blue")
save_message.pack()

# -------------------------------
# Manager Frame Setup
# -------------------------------
manager_frame = tk.Frame(root)
password_list = Treeview(manager_frame, columns=("Username", "Password"), show="headings")
password_list.heading("Username", text="Username")
password_list.heading("Password", text="Password")
password_list.pack(fill="both", expand=True, padx=10, pady=10)
# Login frame for Manager view (centered at the bottom).
manager_login_frame = tk.Frame(manager_frame)
manager_pass_entry = tk.Entry(manager_login_frame, show="*", font=("Arial", 10))
manager_pass_entry.pack(side="left", padx=5)
login_btn = tk.Button(manager_login_frame, text="Login", command=manager_view_login)
login_btn.pack(side="left", padx=5)
login_message = tk.Label(manager_frame, text="", font=("Arial", 10), fg="blue")

# -------------------------------
# Settings Frame Setup
# -------------------------------
settings_frame = tk.Frame(root)

# -------------------------------
# Initialize Default View and Load Data
# -------------------------------
show_analyzer()  # Start with the Analyzer view.
load_passwords_from_csv()  # Load previously saved passwords if any.

# Start the main GUI event loop.
root.mainloop()
