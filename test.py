import tkinter as tk
from tkinter import messagebox
import json
from cryptography.fernet import Fernet
import os
import sys

# Dynamischer Pfad für kompiliertes Bundle
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Aktualisiere die Pfade für key.key und settings.json
KEY_FILE = resource_path("key.key")
SETTINGS_FILE = resource_path("settings.json")

# Generate or load encryption key
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as key_file:
    encryption_key = key_file.read()

cipher = Fernet(encryption_key)

# Load settings if they exist
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "rb") as settings_file:
            encrypted_data = settings_file.read()
            decrypted_data = cipher.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
    return {"user_email": "", "user_password": "", "html_template": ""}

# Save settings to file
def save_settings_to_file(settings):
    encrypted_data = cipher.encrypt(json.dumps(settings).encode())
    with open(SETTINGS_FILE, "wb") as settings_file:
        settings_file.write(encrypted_data)

# Initialize settings
settings = load_settings()
user_email = settings.get("user_email", "")
user_password = settings.get("user_password", "")
html_template = settings.get("html_template", "")

def on_button_click():
    receiver_email = email_entry.get()
    title = title_entry.get()
    message = message_text.get("1.0", tk.END).strip()
    if not receiver_email or not title or not message:
        messagebox.showwarning("Warning", "All fields must be filled!")
    else:
        messagebox.showinfo("Message", f"Email to: {receiver_email}\nTitle: {title}\nMessage: {message}")

def open_settings():
    def save_settings():
        global user_email, user_password, html_template
        user_email = email_entry.get()
        user_password = password_entry.get()
        html_template = template_text.get("1.0", tk.END).strip()
        settings_window.destroy()
        save_settings_to_file({
            "user_email": user_email,
            "user_password": user_password,
            "html_template": html_template
        })
        messagebox.showinfo("Settings", "Settings saved successfully!")

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x400")

    tk.Label(settings_window, text="Your Email:").pack(pady=5)
    email_entry = tk.Entry(settings_window, width=40)
    email_entry.insert(0, user_email)
    email_entry.pack(pady=5)

    tk.Label(settings_window, text="Your Password:").pack(pady=5)
    password_entry = tk.Entry(settings_window, width=40, show="*")
    password_entry.insert(0, user_password)
    password_entry.pack(pady=5)

    tk.Label(settings_window, text="HTML Template:").pack(pady=5)
    template_text = tk.Text(settings_window, width=40, height=10)
    template_text.insert("1.0", html_template)
    template_text.pack(pady=5)

    save_button = tk.Button(settings_window, text="Save Settings", command=save_settings)
    save_button.pack(pady=10)

root = tk.Tk()
root.title("Email Sender App")

# Receiver email input
email_label = tk.Label(root, text="Receiver Email:")
email_label.pack(pady=5)
email_entry = tk.Entry(root, width=40)
email_entry.pack(pady=5)

# Title input
title_label = tk.Label(root, text="Title:")
title_label.pack(pady=5)
title_entry = tk.Entry(root, width=40)
title_entry.pack(pady=5)

# Message textarea
message_label = tk.Label(root, text="Message:")
message_label.pack(pady=5)
message_text = tk.Text(root, width=40, height=10)
message_text.pack(pady=5)

# Submit button
button = tk.Button(root, text="Send Email", command=on_button_click)
button.pack(pady=20)

# Add Settings button with Unicode gear icon (⚙) at the top-right
settings_button = tk.Button(root, text="⚙", command=open_settings, font=("Arial", 14), relief="flat")
settings_button.place(x=460, y=10)  # Position at the top-right corner

root.geometry("500x400")  # Adjust window size for better layout
root.mainloop()
