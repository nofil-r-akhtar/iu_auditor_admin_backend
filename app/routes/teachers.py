from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.teacher import CreateTeacherRequest, UpdateTeacherRequest, UpdateStatusRequest
from app.middleware.auth_middleware import get_current_user
from app.config.database import supabase

router = APIRouter()

# ─── GET ALL TEACHERS ─────────────────────────────────
@router.get("/")
def get_all_teachers(current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("teachers")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Teachers fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch teachers"
        })

# ─── GET TEACHER BY ID ────────────────────────────────
@router.get("/{id}")
def get_teacher_by_id(id: str, current_user: dict = Depends(get_current_user)):
    try:
        result = supabase.table("teachers")\
            .select("*")\
            .eq("id", id)\
            .execute()

        if not result.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Teacher not found"
            })

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Teacher fetched successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch teacher"
        })

# ─── CREATE TEACHER ───────────────────────────────────
@router.post("/")
def create_teacher(data: CreateTeacherRequest, current_user: dict = Depends(get_current_user)):
    try:
        existing = supabase.table("teachers")\
            .select("id")\
            .eq("email", data.email)\
            .execute()

        if existing.data:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Teacher with this email already exists"
            })

        result = supabase.table("teachers").insert({
            "name": data.name,
            "email": data.email,
            "contact_no": data.contact_no,
            "department": data.department,
            "specialization": data.specialization,
            "audit_date": data.audit_date,
            "audit_time": data.audit_time,
            "status": data.status
        }).execute()

        return JSONResponse(status_code=201, content={
            "success": True,
            "message": "Teacher created successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to create teacher"
        })

# ─── UPDATE TEACHER ───────────────────────────────────
@router.put("/{id}")
def update_teacher(id: str, data: UpdateTeacherRequest, current_user: dict = Depends(get_current_user)):
    try:
        existing = supabase.table("teachers")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Teacher not found"
            })

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}

        result = supabase.table("teachers")\
            .update(update_data)\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Teacher updated successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to update teacher"
        })

# ─── UPDATE STATUS ONLY ───────────────────────────────
@router.patch("/{id}/status")
def update_teacher_status(id: str, data: UpdateStatusRequest, current_user: dict = Depends(get_current_user)):
    try:
        existing = supabase.table("teachers")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Teacher not found"
            })

        result = supabase.table("teachers")\
            .update({"status": data.status})\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": f"Teacher status updated to {data.status}",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to update status"
        })

# ─── DELETE TEACHER ───────────────────────────────────
@router.delete("/{id}")
def delete_teacher(id: str, current_user: dict = Depends(get_current_user)):
    try:
        existing = supabase.table("teachers")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "Teacher not found"
            })

        supabase.table("teachers")\
            .delete()\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Teacher deleted successfully"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to delete teacher"
        })