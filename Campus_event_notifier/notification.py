import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from Campus_event_notifier.database import get_db, Event

def send_notification(email: str, subject: str, message: str):
    """
    Send an email notification using Gmail SMTP
    """
    try:
        # Email configuration from environment variables
        sender_email = os.getenv("EMAIL_USERNAME", "your_email@gmail.com")
        sender_password = os.getenv("EMAIL_PASSWORD", "your_app_password")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(message, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login
        server.login(sender_email, sender_password)

        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, email, text)

        # Close connection
        server.quit()

        print(f"✅ Email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def send_event_notification(email: str, event_name: str, event_date: str, event_location: str):
    """
    Send a formatted event notification
    """
    subject = f"Upcoming Event: {event_name}"
    message = f"""
    Hello!

    We have an exciting event coming up:

    📅 Event: {event_name}
    📆 Date: {event_date}
    📍 Location: {event_location}

    Don't miss out! Mark your calendar and join us.

    Best regards,
    Campus Event Notifier Team
    """

    return send_notification(email, subject, message.strip())
