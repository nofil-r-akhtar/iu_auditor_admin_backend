from fastapi import APIRouter, HTTPException
from app.models.user import (
    LoginRequest, ForgotPasswordRequest,
    VerifyOTPRequest, ResendOTPRequest, ChangePasswordRequest
)
from app.services.auth_service import verify_password, create_access_token, hash_password
from app.services.otp_service import send_otp, verify_otp
from app.config.database import supabase

router = APIRouter()

# ─── LOGIN ────────────────────────────────────────────
@router.post("/login")
def login(data: LoginRequest):
    result = supabase.table("users")\
        .select("*")\
        .eq("email", data.email)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=404, 
            success = "false",
            detail= "Invalid email or passowrd")

    user = result.data[0]

    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, success = "false", detail="Invalid password")

    token = create_access_token({
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "success": "true",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

# ─── FORGOT PASSWORD ──────────────────────────────────
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    result = supabase.table("users")\
        .select("id, email")\
        .eq("email", data.email)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, success = "false", detail="Email not found")

    user = result.data[0]
    send_otp(user["email"], "forgot_password", user["id"])

    return {
        "success": "true",
        "message": "OTP sent to your email"}

# ─── VERIFY OTP ───────────────────────────────────────
@router.post("/verify-otp")
def verify_otp_route(data: VerifyOTPRequest):
    success, message = verify_otp(data.email, data.otp_code, "forgot_password")

    if not success:
        raise HTTPException(status_code=400, success = "false", detail=message)

    return {"success": "true", "message": message, "verified": True}

# ─── RESEND OTP ───────────────────────────────────────
@router.post("/resend-otp")
def resend_otp(data: ResendOTPRequest):
    result = supabase.table("users")\
        .select("id, email")\
        .eq("email", data.email)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, success = "false", detail="Email not found")

    user = result.data[0]
    send_otp(user["email"], "forgot_password", user["id"])

    return {
        "success": "true",
        "message": "New OTP sent to your email"}

# ─── CHANGE PASSWORD ──────────────────────────────────
@router.post("/change-password")
def change_password(data: ChangePasswordRequest):
    success, message = verify_otp(data.email, data.otp_code, "forgot_password")

    if not success:
        raise HTTPException(status_code=400, success = false, detail=message)

    new_hash = hash_password(data.new_password)

    supabase.table("users")\
        .update({"password_hash": new_hash})\
        .eq("email", data.email)\
        .execute()

    return {
        "success": "true",
        "message": "Password changed successfully ✅"}