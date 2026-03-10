from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.audit_review import CreateReviewRequest, SubmitReviewRequest
from app.middleware.auth_middleware import get_current_user
from app.config.database import supabase

router = APIRouter()

# ─── ADMIN ONLY ───────────────────────────────────────
def admin_only(current_user: dict = Depends(get_current_user)):
    from fastapi import HTTPException
    if current_user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

# ══════════════════════════════════════════════════════
#  ADMIN APIS
# ══════════════════════════════════════════════════════

# ─── GET ALL REVIEWS ──────────────────────────────────
@router.get("/")
def get_all_reviews(current_user: dict = Depends(admin_only)):
    try:
        result = supabase.table("audit_reviews")\
            .select("*, teachers(name, email, department), audit_forms(title, department), users(name, email)")\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Reviews fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch reviews"
        })

# ─── GET REVIEW BY ID WITH FULL REPORT ────────────────
@router.get("/{id}")
def get_review_by_id(id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Get review with related data
        review = supabase.table("audit_reviews")\
            .select("*, teachers(name, email, department, specialization), audit_forms(title, department), users(name, email)")\
            .eq("id", id)\
            .execute()

        if not review.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Review not found"
            })

        # Get answers with questions
        answers = supabase.table("audit_answers")\
            .select("*, audit_questions(question_text, question_type, options)")\
            .eq("review_id", id)\
            .execute()

        review_data = review.data[0]
        review_data["answers"] = answers.data

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Review fetched successfully",
            "data": review_data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch review"
        })

# ─── GET REVIEWS BY TEACHER ───────────────────────────
@router.get("/teacher/{teacher_id}")
def get_reviews_by_teacher(teacher_id: str, current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("audit_reviews")\
            .select("*, audit_forms(title, department), users(name, email)")\
            .eq("teacher_id", teacher_id)\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Teacher reviews fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch teacher reviews"
        })

# ─── CREATE REVIEW (ADMIN ASSIGNS TO SENIOR LECTURER) ─
@router.post("/")
def create_review(data: CreateReviewRequest, current_user: dict = Depends(admin_only)):
    try:
        # Check teacher exists
        teacher = supabase.table("teachers")\
            .select("id")\
            .eq("id", data.teacher_id)\
            .execute()

        if not teacher.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Teacher not found"
            })

        # Check form exists
        form = supabase.table("audit_forms")\
            .select("id")\
            .eq("id", data.form_id)\
            .execute()

        if not form.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Audit form not found"
            })

        result = supabase.table("audit_reviews").insert({
            "teacher_id": data.teacher_id,
            "form_id": data.form_id,
            "reviewed_by": current_user["sub"],
            "status": "pending",
            "notes": data.notes
        }).execute()

        return JSONResponse(status_code=201, content={
            "success": True,
            "message": "Audit review created successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to create review"
        })

# ─── DELETE REVIEW ────────────────────────────────────
@router.delete("/{id}")
def delete_review(id: str, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("audit_reviews")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Review not found"
            })

        supabase.table("audit_reviews")\
            .delete()\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Review deleted successfully"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to delete review"
        })

# ══════════════════════════════════════════════════════
#  SENIOR LECTURER APIS
# ══════════════════════════════════════════════════════

# ─── GET MY ASSIGNED REVIEWS ──────────────────────────
@router.get("/my/reviews")
def get_my_reviews(current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("audit_reviews")\
            .select("*, teachers(name, email, department), audit_forms(title, department)")\
            .eq("reviewed_by", current_user["sub"])\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Your reviews fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch your reviews"
        })

# ─── SUBMIT REVIEW WITH ANSWERS ───────────────────────
@router.post("/{id}/submit")
def submit_review(id: str, data: SubmitReviewRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Check review exists and belongs to current user
        review = supabase.table("audit_reviews")\
            .select("*")\
            .eq("id", id)\
            .eq("reviewed_by", current_user["sub"])\
            .execute()

        if not review.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Review not found or not assigned to you"
            })

        if review.data[0]["status"] == "completed":
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Review already completed"
            })

        # Save all answers
        for answer in data.answers:
            supabase.table("audit_answers").insert({
                "review_id": id,
                "question_id": answer.question_id,
                "answer_text": answer.answer_text,
                "answer_rating": answer.answer_rating,
                "answer_mcq": answer.answer_mcq,
                "answer_yes_no": answer.answer_yes_no
            }).execute()

        # Mark review as completed
        supabase.table("audit_reviews")\
            .update({
                "status": "completed",
                "notes": data.notes
            })\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Review submitted successfully ✅"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to submit review"
        })