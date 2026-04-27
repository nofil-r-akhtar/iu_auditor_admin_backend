"""
Email sending via Brevo HTTP API.
Use `send_email_async(...)` for fire-and-forget — failures are logged but
won't break the API request that triggered the email.
"""
import requests
import logging
import os
import threading


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Synchronous send. Returns True/False — won't raise on failure.
    Useful for the few places we *want* to know if it failed (e.g. OTP).
    """
    try:
        BREVO_API_KEY = os.getenv("SMTP_API_KEY")
        SMTP_FROM     = os.getenv("SMTP_FROM")

        if not BREVO_API_KEY:
            logging.warning("SMTP_API_KEY not set — skipping email send")
            return False

        logging.info(f"Sending email to {to_email}...")

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept":       "application/json",
            "content-type": "application/json",
            "api-key":      BREVO_API_KEY,
        }
        payload = {
            "sender":      {"name": "IU Auditor", "email": SMTP_FROM},
            "to":          [{"email": to_email}],
            "subject":     subject,
            "htmlContent": body,
        }

        response = requests.post(url, json=payload,
                                 headers=headers, timeout=30)
        if response.status_code == 201:
            logging.info(f"✅ Email sent to {to_email}")
            return True

        logging.error(f"❌ Brevo API error: {response.status_code} - {response.text}")
        return False

    except Exception as e:
        logging.error(f"❌ Email error sending to {to_email}: {e}")
        return False


def send_email_async(to_email: str, subject: str, body: str) -> None:
    """
    Fire-and-forget send. Spawns a background thread so the calling endpoint
    returns immediately even if SMTP is slow or fails.
    Failures are logged but never raised — the user-facing action (creating
    a teacher / assigning an audit) succeeds regardless.
    """
    def _worker():
        try:
            send_email(to_email, subject, body)
        except Exception as e:
            logging.error(f"Async email failed for {to_email}: {e}")

    threading.Thread(target=_worker, daemon=True).start()