from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class TeacherStatus(str, Enum):
    pending = "pending"
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"

class CreateTeacherRequest(BaseModel):
    name: str
    email: EmailStr
    contact_no: str
    department: str
    specialization: str
    audit_date: Optional[str] = None   # format: "2026-03-15"
    audit_time: Optional[str] = None   # format: "14:30:00"
    status: TeacherStatus = TeacherStatus.pending

class UpdateTeacherRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_no: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    audit_date: Optional[str] = None   # format: "2026-03-15"
    audit_time: Optional[str] = None   # format: "14:30:00"
    status: Optional[TeacherStatus] = None

class UpdateStatusRequest(BaseModel):
    status: TeacherStatus