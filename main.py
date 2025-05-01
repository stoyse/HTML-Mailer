import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sys
import webbrowser
from cryptography.fernet import Fernet, InvalidToken  # Add InvalidToken to the import
from smtp_sender import send_email  # This must be in the same folder

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Paths inside the bundle
KEY_FILE = resource_path("key.key")
SETTINGS_FILE = resource_path("settings.json")
HTML_TEMPLATE_FILE = resource_path("template.html")

# Generate encryption key if missing
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        key = Fernet.generate_key()
        f.write(key)

# Validate and load the encryption key
try:
    with open(KEY_FILE, "rb") as f:
        encryption_key = f.read()
        if len(encryption_key) != 44:  # Fernet keys are 44 characters long (32 bytes base64-encoded)
            raise ValueError("Invalid Fernet key.")
        cipher = Fernet(encryption_key)
except (ValueError, Exception):
    # Regenerate the key if invalid or corrupted
    with open(KEY_FILE, "wb") as f:
        encryption_key = Fernet.generate_key()
        f.write(encryption_key)
    cipher = Fernet(encryption_key)

# Load and save settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "rb") as f:
                decrypted = cipher.decrypt(f.read()).decode()
                return json.loads(decrypted)
        except (InvalidToken, json.JSONDecodeError):  # Use the imported InvalidToken
            # Handle invalid or corrupted settings file
            messagebox.showwarning("Settings Error", "Settings file is corrupted. Resetting to default.")
            save_settings_to_file({"user_email": "", "user_password": ""})
    return {"user_email": "", "user_password": ""}

def save_settings_to_file(settings):
    with open(SETTINGS_FILE, "wb") as f:
        f.write(cipher.encrypt(json.dumps(settings).encode()))

def load_html_template():
    if os.path.exists(HTML_TEMPLATE_FILE):
        with open(HTML_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_html_template(content):
    with open(HTML_TEMPLATE_FILE, "w", encoding="utf-8") as f:
        f.write(content)

# Initialize
settings = load_settings()
user_email = settings.get("user_email", "")
user_password = settings.get("user_password", "")
html_template = load_html_template()

attachment_path = None  # Global variable to store the attachment path

def show_app_password_help():
    messagebox.showinfo(
        "App Password Help",
        "If you use Gmail with 2FA, you'll need an App Password.\n"
        "1. Go to your Google Account\n"
        "2. Enable 2FA under 'Security'\n"
        "3. Scroll to 'App Passwords'\n"
        "4. Generate one for Mail\n"
        "5. Use it here instead of your main password"
    )
    webbrowser.open("https://myaccount.google.com/apppasswords")

def upload_file():
    global attachment_path
    attachment_path = filedialog.askopenfilename()
    if attachment_path:
        attachment_label.config(text=f"Attachment: {os.path.basename(attachment_path)}")

def on_send_click():
    receiver = email_entry.get()
    title = title_entry.get()
    message = message_text.get("1.0", tk.END).strip()

    # Replace newlines with <br> for HTML compatibility
    formatted_message = message.replace("\n", "<br>")

    if not receiver or not title or not message:
        messagebox.showwarning("Missing Fields", "Please fill in all fields.")
        return
    if not user_email or not user_password:
        messagebox.showwarning("Missing Settings", "Set your email and password first.")
        return

    try:
        send_email(user_email, user_password, receiver, title, formatted_message, attachment_path)
        messagebox.showinfo("Success", "Email sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        if "Application-specific password required" in str(e):
            show_app_password_help()

def open_settings():
    def save_settings():
        global user_email, user_password, html_template
        user_email = email_entry_settings.get()
        user_password = password_entry_settings.get()
        html_template = template_text.get("1.0", tk.END).strip()
        save_settings_to_file({"user_email": user_email, "user_password": user_password})
        save_html_template(html_template)
        messagebox.showinfo("Saved", "Settings saved.")
        settings_window.destroy()

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x400")

    tk.Label(settings_window, text="Your Email:").pack(pady=5)
    email_entry_settings = tk.Entry(settings_window, width=40)
    email_entry_settings.insert(0, user_email)
    email_entry_settings.pack(pady=5)

    tk.Label(settings_window, text="Password (App Password):").pack(pady=5)
    password_entry_settings = tk.Entry(settings_window, width=40, show="*")
    password_entry_settings.insert(0, user_password)
    password_entry_settings.pack(pady=5)

    tk.Label(settings_window, text="HTML Template:").pack(pady=5)
    template_text = tk.Text(settings_window, width=40, height=10)
    template_text.insert("1.0", html_template)
    template_text.pack(pady=5)

    tk.Button(settings_window, text="App Password Help", command=show_app_password_help).pack(pady=5)
    tk.Button(settings_window, text="Save", command=save_settings).pack(pady=10)

# GUI setup
root = tk.Tk()
root.title("HTML Email Sender")
root.geometry("600x450")

tk.Label(root, text="Receiver Email:").pack(pady=5)
email_entry = tk.Entry(root, width=40)
email_entry.pack(pady=5)

tk.Label(root, text="Subject:").pack(pady=5)
title_entry = tk.Entry(root, width=40)
title_entry.pack(pady=5)

tk.Label(root, text="Message:").pack(pady=5)
message_text = tk.Text(root, width=40, height=10)
message_text.pack(pady=5)

tk.Button(root, text="Upload File", command=upload_file).pack(pady=5)

attachment_label = tk.Label(root, text="No attachment selected")
attachment_label.pack(pady=5)

tk.Button(root, text="Send Email", command=on_send_click).pack(pady=10)
tk.Button(root, text="⚙ Settings", command=open_settings).place(x=500, y=10)

root.mainloop()