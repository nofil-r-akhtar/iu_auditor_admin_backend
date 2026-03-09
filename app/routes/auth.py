from app.middleware.auth_middleware import get_current_user
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.models.user import (
    LoginRequest, ForgotPasswordRequest,
    VerifyOTPRequest, ResendOTPRequest, ChangePasswordRequest, FirstLoginChangePassword
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
        return JSONResponse(status_code=404, content={
            "success": False,
            "message": "Invalid email or password"
        })

    user = result.data[0]

    if not verify_password(data.password, user["password_hash"]):
        return JSONResponse(status_code=401, content={
            "success": False,
            "message": "Invalid email or password"
        })

    token = create_access_token({
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"]
    })

    return JSONResponse(status_code=200, content={
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "must_change_password": user["must_change_password"],
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    })

# ─── FORGOT PASSWORD ──────────────────────────────────
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    result = supabase.table("users")\
        .select("id, email")\
        .eq("email", data.email)\
        .execute()

    if not result.data:
        return JSONResponse(status_code=404, content={
            "success": False,
            "message": "No account found with this email address"
        })

    user = result.data[0]
    send_otp(user["email"], "forgot_password", user["id"])

    return JSONResponse(status_code=200, content={
        "success": True,
        "message": "OTP sent to your email"
    })

# ─── VERIFY OTP ───────────────────────────────────────
@router.post("/verify-otp")
def verify_otp_route(data: VerifyOTPRequest):
    # check only — don't mark as used yet!
    success, message = verify_otp(data.email, data.otp_code, "forgot_password", mark_used=False)

    if not success:
        return JSONResponse(status_code=400, content={
            "success": False,
            "message": message
        })

    return JSONResponse(status_code=200, content={
        "success": True,
        "message": "OTP verified successfully",
        "verified": True
    })

# ─── RESEND OTP ───────────────────────────────────────
@router.post("/resend-otp")
def resend_otp(data: ResendOTPRequest):
    result = supabase.table("users")\
        .select("id, email")\
        .eq("email", data.email)\
        .execute()

    if not result.data:
        return JSONResponse(status_code=404, content={
            "success": False,
            "message": "No account found with this email address"
        })

    user = result.data[0]
    send_otp(user["email"], "forgot_password", user["id"])

    return JSONResponse(status_code=200, content={
        "success": True,
        "message": "New OTP sent to your email"
    })

# ─── CHANGE PASSWORD ──────────────────────────────────
@router.post("/change-password")
def change_password(data: ChangePasswordRequest):
    # mark as used here — final step!
    success, message = verify_otp(data.email, data.otp_code, "forgot_password", mark_used=True)

    if not success:
        return JSONResponse(status_code=400, content={
            "success": False,
            "message": message
        })

    new_hash = hash_password(data.new_password)

    supabase.table("users")\
        .update({"password_hash": new_hash})\
        .eq("email", data.email)\
        .execute()

    return JSONResponse(status_code=200, content={
        "success": True,
        "message": "Password changed successfully"
    })

# ─── ME ───────────────────────────────────────────────
@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("users")\
            .select("id, name, email, role, created_at")\
            .eq("id", current_user["sub"])\
            .execute()

        if not result.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "User not found"
            })

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Profile fetched successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch profile"
        })

# ─── FIRST LOGIN CHANGE PASSWORD ──────────────────────
@router.post("/first-login-change-password")
def first_login_change_password(data: FirstLoginChangePassword):
    try:
        # Fetch user
        result = supabase.table("users")\
            .select("*")\
            .eq("email", data.email)\
            .execute()

        if not result.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "User not found"
            })

        user = result.data[0]

        # Verify old password
        if not verify_password(data.old_password, user["password_hash"]):
            return JSONResponse(status_code=401, content={
                "success": False,
                "message": "Old password is incorrect"
            })

        # Check must_change_password flag
        if not user["must_change_password"]:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Password change not required"
            })

        # Hash and update new password
        new_hash = hash_password(data.new_password)

        supabase.table("users")\
            .update({
                "password_hash": new_hash,
                "must_change_password": False  # ← turn off flag
            })\
            .eq("email", data.email)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Password changed successfully. Please login again."
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to change password"
        })