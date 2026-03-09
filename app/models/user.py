from pydantic import BaseModel, EmailStr
from typing import Optional

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

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "senior_lecturer"
    department: Optional[str] = None

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None

class FirstLoginChangePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str