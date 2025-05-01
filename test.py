import tkinter as tk
from tkinter import messagebox
import json
from cryptography.fernet import Fernet
import os
import sys
import webbrowser
from smtp_sender import send_email  # Import the send_email function

# Dynamischer Pfad für kompiliertes Bundle
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Aktualisiere die Pfade für key.key und settings.json
KEY_FILE = resource_path("key.key")
SETTINGS_FILE = resource_path("settings.json")

# Update paths for the HTML template file
HTML_TEMPLATE_FILE = resource_path("template.html")

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
    return {"user_email": "", "user_password": ""}

# Save settings to file
def save_settings_to_file(settings):
    encrypted_data = cipher.encrypt(json.dumps(settings).encode())
    with open(SETTINGS_FILE, "wb") as settings_file:
        settings_file.write(encrypted_data)

# Save HTML template to a file
def save_html_template(template_content):
    with open(HTML_TEMPLATE_FILE, "w", encoding="utf-8") as template_file:
        template_file.write(template_content)

# Load HTML template from a file
def load_html_template():
    if os.path.exists(HTML_TEMPLATE_FILE):
        with open(HTML_TEMPLATE_FILE, "r", encoding="utf-8") as template_file:
            return template_file.read()
    return ""

# Initialize settings
settings = load_settings()
user_email = settings.get("user_email", "")
user_password = settings.get("user_password", "")
html_template = load_html_template()

def show_app_password_help():
    messagebox.showinfo("App-Passwort benötigt", 
                        "Für Gmail mit 2-Faktor-Authentifizierung benötigst du ein App-Passwort anstelle deines regulären Passworts.\n\n"
                        "1. Gehe zu deinem Google-Konto\n"
                        "2. Wähle 'Sicherheit' → '2-Faktor-Authentifizierung'\n"
                        "3. Scrolle nach unten zu 'App-Passwörter'\n"
                        "4. Erstelle ein neues App-Passwort für 'Mail' und 'Anderes (eigenen Namen angeben)'\n"
                        "5. Kopiere das 16-stellige Passwort und verwende es in den Einstellungen")
    webbrowser.open("https://myaccount.google.com/apppasswords")

def on_button_click():
    receiver_email = email_entry.get()
    title = title_entry.get()
    message = message_text.get("1.0", tk.END).strip()
    
    # Check if all fields are filled
    if not receiver_email or not title or not message:
        messagebox.showwarning("Warning", "All fields must be filled!")
        return
        
    # Check if sender credentials are set
    if not user_email or not user_password:
        messagebox.showwarning("Warning", "Please set your email and password in Settings first!")
        return
        
    try:
        send_email(user_email, user_password, receiver_email, title, message)
        messagebox.showinfo("Success", "Email sent successfully!")
    except Exception as e:
        error_msg = str(e)
        messagebox.showerror("Error", error_msg)
        # Check for app password error
        if "Application-specific password required" in error_msg:
            show_app_password_help()

def open_settings():
    def save_settings():
        global user_email, user_password, html_template
        user_email = email_entry.get()
        user_password = password_entry.get()
        html_template = template_text.get("1.0", tk.END).strip()
        settings_window.destroy()
        save_settings_to_file({
            "user_email": user_email,
            "user_password": user_password
        })
        save_html_template(html_template)
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

    help_button = tk.Button(settings_window, text="Hilfe zu App-Passwörtern", command=show_app_password_help)
    help_button.pack(pady=5)
    
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