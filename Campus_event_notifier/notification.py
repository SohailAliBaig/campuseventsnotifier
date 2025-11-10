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
        sender_email = os.getenv("EMAIL_USERNAME")
        sender_password = os.getenv("EMAIL_PASSWORD")

        if not sender_email or not sender_password:
            print("❌ Email configuration missing. Check EMAIL_USERNAME and EMAIL_PASSWORD in .env")
            return False

        print(f"📧 Attempting to send email from {sender_email} to {email}")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"Campus Events <{sender_email}>"
        msg['To'] = email
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(message, 'plain'))

        try:
            # Create SMTP session
            print("📨 Connecting to Gmail SMTP server...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            # Login
            print("🔐 Attempting to login...")
            server.login(sender_email, sender_password)
            print("✅ Login successful")

            # Send email
            text = msg.as_string()
            print("📤 Sending email...")
            server.sendmail(sender_email, email, text)

            # Close connection
            server.quit()
            print(f"✅ Email sent successfully to {email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication failed. Check your email and app password")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error occurred: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False

    except Exception as e:
        print(f"❌ Error in send_notification: {str(e)}")
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
