from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.audit import (
    CreateFormRequest, UpdateFormRequest,
    CreateQuestionRequest, UpdateQuestionRequest
)
from app.middleware.auth_middleware import get_current_user
from app.config.database import supabase

router = APIRouter()

# ─── ADMIN ONLY MIDDLEWARE ────────────────────────────
def admin_only(current_user: dict = Depends(get_current_user)):
    from fastapi import HTTPException
    if current_user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

# ══════════════════════════════════════════════════════
#  FORMS
# ══════════════════════════════════════════════════════

# ─── GET ALL FORMS ────────────────────────────────────
@router.get("/forms")
def get_all_forms(current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("audit_forms")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Forms fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch forms"
        })

# ─── GET FORMS BY DEPARTMENT ──────────────────────────
@router.get("/forms/department/{department}")
def get_forms_by_department(department: str, current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("audit_forms")\
            .select("*")\
            .eq("department", department)\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": f"Forms for {department} fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch forms"
        })

# ─── GET FORM BY ID ───────────────────────────────────
@router.get("/forms/{id}")
def get_form_by_id(id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Get form
        form = supabase.table("audit_forms")\
            .select("*")\
            .eq("id", id)\
            .execute()

        if not form.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Form not found"
            })

        # Get questions for this form
        questions = supabase.table("audit_questions")\
            .select("*")\
            .eq("form_id", id)\
            .execute()

        form_data = form.data[0]
        form_data["questions"] = questions.data

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Form fetched successfully",
            "data": form_data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch form"
        })

# ─── CREATE FORM ──────────────────────────────────────
@router.post("/forms")
def create_form(data: CreateFormRequest, current_user: dict = Depends(admin_only)):
    try:
        result = supabase.table("audit_forms").insert({
            "title": data.title,
            "description": data.description,
            "department": data.department,
            "is_active": data.is_active,
            "created_by": current_user["sub"]
        }).execute()

        return JSONResponse(status_code=201, content={
            "success": True,
            "message": "Form created successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to create form"
        })

# ─── UPDATE FORM ──────────────────────────────────────
@router.put("/forms/{id}")
def update_form(id: str, data: UpdateFormRequest, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("audit_forms")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Form not found"
            })

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}

        result = supabase.table("audit_forms")\
            .update(update_data)\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Form updated successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to update form"
        })

# ─── DELETE FORM ──────────────────────────────────────
@router.delete("/forms/{id}")
def delete_form(id: str, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("audit_forms")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Form not found"
            })

        supabase.table("audit_forms")\
            .delete()\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Form deleted successfully"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to delete form"
        })

# ══════════════════════════════════════════════════════
#  QUESTIONS
# ══════════════════════════════════════════════════════

# ─── GET ALL QUESTIONS FOR A FORM ─────────────────────
@router.get("/forms/{form_id}/questions")
def get_questions(form_id: str, current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("audit_questions")\
            .select("*")\
            .eq("form_id", form_id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Questions fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch questions"
        })

# ─── ADD QUESTION TO FORM ─────────────────────────────
@router.post("/forms/{form_id}/questions")
def add_question(form_id: str, data: CreateQuestionRequest, current_user: dict = Depends(admin_only)):
    try:
        # Check form exists
        form = supabase.table("audit_forms")\
            .select("id")\
            .eq("id", form_id)\
            .execute()

        if not form.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Form not found"
            })

        # MCQ must have options
        if data.question_type == "mcq" and not data.options:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "MCQ questions must have options"
            })

        result = supabase.table("audit_questions").insert({
            "form_id": form_id,
            "question_text": data.question_text,
            "question_type": data.question_type,
            "options": data.options,
            "is_required": data.is_required
        }).execute()

        return JSONResponse(status_code=201, content={
            "success": True,
            "message": "Question added successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to add question"
        })

# ─── UPDATE QUESTION ──────────────────────────────────
@router.put("/forms/{form_id}/questions/{question_id}")
def update_question(form_id: str, question_id: str, data: UpdateQuestionRequest, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("audit_questions")\
            .select("id")\
            .eq("id", question_id)\
            .eq("form_id", form_id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Question not found"
            })

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}

        result = supabase.table("audit_questions")\
            .update(update_data)\
            .eq("id", question_id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Question updated successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to update question"
        })

# ─── DELETE QUESTION ──────────────────────────────────
@router.delete("/forms/{form_id}/questions/{question_id}")
def delete_question(form_id: str, question_id: str, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("audit_questions")\
            .select("id")\
            .eq("id", question_id)\
            .eq("form_id", form_id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Question not found"
            })

        supabase.table("audit_questions")\
            .delete()\
            .eq("id", question_id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Question deleted successfully"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to delete question"
        })