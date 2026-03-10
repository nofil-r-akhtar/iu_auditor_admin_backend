from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class QuestionType(str, Enum):
    rating = "rating"
    paragraph = "paragraph"
    mcq = "mcq"
    yes_no = "yes_no"

# ─── FORM MODELS ──────────────────────────────────────
class CreateFormRequest(BaseModel):
    title: str
    description: Optional[str] = None
    department: str
    is_active: bool = True

class UpdateFormRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

# ─── QUESTION MODELS ──────────────────────────────────
class CreateQuestionRequest(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None  # only for MCQ
    is_required: bool = True

class UpdateQuestionRequest(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    is_required: Optional[bool] = None