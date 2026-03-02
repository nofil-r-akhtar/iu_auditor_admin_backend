import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False