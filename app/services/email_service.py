import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

def send_email(to_email: str, subject: str, body: str):
    try:
        logging.info(f"Sending email to {to_email}...")
        logging.info(f"SMTP Host: {SMTP_HOST}, Port: {SMTP_PORT}")
        logging.info(f"SMTP User: {SMTP_USER}")

        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.set_debuglevel(1)   # shows SMTP conversation in logs
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())

        logging.info(f"✅ Email sent to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logging.error("❌ SMTP Authentication failed - check username/password")
        return False
    except smtplib.SMTPConnectError:
        logging.error("❌ SMTP Connection failed - check host/port")
        return False
    except smtplib.SMTPException as e:
        logging.error(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        logging.error(f"❌ Email error: {e}")
        return False