from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str

class ResendOTPRequest(BaseModel):
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str