from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class AuditReviewStatus(str, Enum):
    pending = "pending"
    completed = "completed"

class AnswerRequest(BaseModel):
    question_id: str
    answer_text: Optional[str] = None
    answer_rating: Optional[int] = None
    answer_mcq: Optional[str] = None
    answer_yes_no: Optional[bool] = None

class CreateReviewRequest(BaseModel):
    teacher_id: str
    form_id: str
    notes: Optional[str] = None

class SubmitReviewRequest(BaseModel):
    notes: Optional[str] = None
    answers: List[AnswerRequest]