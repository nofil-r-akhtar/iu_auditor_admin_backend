import requests
import logging
import os

def send_email(to_email: str, subject: str, body: str):
    try:
        BREVO_API_KEY = os.getenv("SMTP_API_KEY")
        SMTP_FROM = os.getenv("SMTP_FROM")

        logging.info(f"Sending email to {to_email} via Brevo API...")

        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": BREVO_API_KEY
        }

        payload = {
            "sender": {
                "name": "IU Auditor",
                "email": SMTP_FROM
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": body
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 201:
            logging.info(f"✅ Email sent to {to_email}")
            return True
        else:
            logging.error(f"❌ Brevo API error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logging.error(f"❌ Email error: {e}")
        return False