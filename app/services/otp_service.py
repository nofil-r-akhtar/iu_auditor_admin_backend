import random
import string
from datetime import datetime, timedelta, timezone
from app.config.database import supabase
from app.services.email_service import send_email

def generate_otp(length=4):
    return ''.join(random.choices(string.digits, k=length))

def send_otp(email: str, otp_type: str, user_id: str):
    # Invalidate all previous unused OTPs
    supabase.table("otp_verifications")\
        .update({"is_used": True})\
        .eq("email", email)\
        .eq("otp_type", otp_type)\
        .eq("is_used", False)\
        .execute()

    # Generate new OTP
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Save to database
    supabase.table("otp_verifications").insert({
        "user_id": user_id,
        "email": email,
        "otp_code": otp_code,
        "otp_type": otp_type,
        "is_used": False,
        "expires_at": expires_at.isoformat()
    }).execute()

    # Send email
    subject = "Your OTP Code - IU Auditor"
    body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 400px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #4F46E5;">IU Auditor</h2>
            <p>Use the OTP code below. It expires in <b>10 minutes</b>.</p>
            <h1 style="color: #4F46E5; letter-spacing: 8px; text-align: center;">{otp_code}</h1>
            <p style="color: #999; font-size: 12px;">If you didn't request this, please ignore this email.</p>
        </div>
    """
    send_email(email, subject, body)
    return True

def verify_otp(email: str, otp_code: str, otp_type: str):
    result = supabase.table("otp_verifications")\
        .select("*")\
        .eq("email", email)\
        .eq("otp_code", otp_code)\
        .eq("otp_type", otp_type)\
        .eq("is_used", False)\
        .execute()

    if not result.data:
        return False, "Invalid OTP"

    otp = result.data[0]

    # Check expiry
    expires_at = datetime.fromisoformat(otp["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return False, "OTP has expired"

    # Mark as used
    supabase.table("otp_verifications")\
        .update({"is_used": True})\
        .eq("id", otp["id"])\
        .execute()

    return True, "OTP verified"