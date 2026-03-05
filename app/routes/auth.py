from fastapi import APIRouter, HTTPException
from app.models.user import (
    LoginRequest, ForgotPasswordRequest,
    VerifyOTPRequest, ResendOTPRequest, ChangePasswordRequest
)
from app.services.auth_service import verify_password, create_access_token, hash_password
from app.services.otp_service import send_otp, verify_otp
from app.config.database import supabase

router = APIRouter()

# ─── HELPER ───────────────────────────────────────────
def success_response(data: dict, message: str = "Success", status_code: int = 200):
    return JSONResponse(status_code=status_code, content={
        "success": True,
        "message": message,
        "data": data
    })

def error_response(message: str, status_code: int, error_code: str = None):
    raise HTTPException(status_code=status_code, detail={
        "success": False,
        "message": message,
        "error_code": error_code,
    })

# ─── LOGIN ────────────────────────────────────────────
@router.post("/login")
def login(data: LoginRequest):
    try:
        result = supabase.table("users")\
            .select("*")\
            .eq("email", data.email)\
            .execute()

        if not result.data:
            error_response(
                message="No account found with this email address",
                status_code=404,
                error_code="USER_NOT_FOUND"
            )

        user = result.data[0]

        if not verify_password(data.password, user["password_hash"]):
            error_response(
                message="Incorrect password. Please try again",
                status_code=401,
                error_code="INVALID_PASSWORD"
            )

        token = create_access_token({
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        })

        return success_response(
            message="Login successful",
            data={
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        error_response(
            message="Something went wrong during login. Please try again",
            status_code=500,
            error_code="LOGIN_FAILED"
        )

# ─── FORGOT PASSWORD ──────────────────────────────────
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    try:
        result = supabase.table("users")\
            .select("id, email")\
            .eq("email", data.email)\
            .execute()

        if not result.data:
            error_response(
                message="No account found with this email address",
                status_code=404,
                error_code="EMAIL_NOT_FOUND"
            )

        user = result.data[0]
        send_otp(user["email"], "forgot_password", user["id"])

        return success_response(
            message="OTP sent successfully to your email",
            data={"email": user["email"]}
        )

    except HTTPException:
        raise
    except Exception as e:
        error_response(
            message="Failed to send OTP. Please try again",
            status_code=500,
            error_code="OTP_SEND_FAILED"
        )

# ─── VERIFY OTP ───────────────────────────────────────
@router.post("/verify-otp")
def verify_otp_route(data: VerifyOTPRequest):
    try:
        success, message = verify_otp(data.email, data.otp_code, "forgot_password")

        if not success:
            error_response(
                message=message,
                status_code=400,
                error_code="OTP_INVALID" if "Invalid" in message else "OTP_EXPIRED"
            )

        return success_response(
            message="OTP verified successfully",
            data={"verified": True, "email": data.email}
        )

    except HTTPException:
        raise
    except Exception as e:
        error_response(
            message="OTP verification failed. Please try again",
            status_code=500,
            error_code="OTP_VERIFICATION_FAILED"
        )

# ─── RESEND OTP ───────────────────────────────────────
@router.post("/resend-otp")
def resend_otp(data: ResendOTPRequest):
    try:
        result = supabase.table("users")\
            .select("id, email")\
            .eq("email", data.email)\
            .execute()

        if not result.data:
            error_response(
                message="No account found with this email address",
                status_code=404,
                error_code="EMAIL_NOT_FOUND"
            )

        user = result.data[0]
        send_otp(user["email"], "forgot_password", user["id"])

        return success_response(
            message="New OTP sent successfully to your email",
            data={"email": user["email"]}
        )

    except HTTPException:
        raise
    except Exception as e:
        error_response(
            message="Failed to resend OTP. Please try again",
            status_code=500,
            error_code="OTP_RESEND_FAILED"
        )

# ─── CHANGE PASSWORD ──────────────────────────────────
@router.post("/change-password")
def change_password(data: ChangePasswordRequest):
    try:
        success, message = verify_otp(data.email, data.otp_code, "forgot_password")

        if not success:
            error_response(
                message=message,
                status_code=400,
                error_code="OTP_INVALID" if "Invalid" in message else "OTP_EXPIRED"
            )

        new_hash = hash_password(data.new_password)

        supabase.table("users")\
            .update({"password_hash": new_hash})\
            .eq("email", data.email)\
            .execute()

        return success_response(
            message="Password changed successfully",
            data={"email": data.email}
        )

    except HTTPException:
        raise
    except Exception as e:
        error_response(
            message="Failed to change password. Please try again",
            status_code=500,
            error_code="PASSWORD_CHANGE_FAILED"
        )