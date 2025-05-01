import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys

# Dynamischer Pfad für kompiliertes Bundle
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Update path for the HTML template file
HTML_TEMPLATE_FILE = resource_path("template.html")

def send_email(sender_email, sender_password, receiver_email, subject, message):
    # Load the HTML template
    if not os.path.exists(HTML_TEMPLATE_FILE):
        raise FileNotFoundError(f"Template file '{HTML_TEMPLATE_FILE}' not found.")
    
    with open(HTML_TEMPLATE_FILE, "r", encoding="utf-8") as template_file:
        html_template = template_file.read()

    # Replace {message} placeholder in the template
    html_content = html_template.replace("{message}", message)

    # Create the email
    email = MIMEMultipart("alternative")
    email["From"] = sender_email
    email["To"] = receiver_email
    email["Subject"] = subject

    # Attach the HTML content
    email.attach(MIMEText(html_content, "html"))

    # Send the email using SMTP
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, email.as_string())
            return True
    except Exception as e:
        # Raise the exception instead of just printing it
        raise Exception(f"Failed to send email: {str(e)}")
