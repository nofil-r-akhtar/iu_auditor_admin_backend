from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.models.user import CreateUserRequest, UpdateUserRequest
from app.middleware.auth_middleware import get_current_user
from app.services.auth_service import hash_password
from app.config.database import supabase

router = APIRouter()

# ─── MIDDLEWARE: ADMIN/SUPER ADMIN ONLY ───────────────
def admin_only(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

# ─── GET ALL USERS ────────────────────────────────────
@router.get("/users")
def get_all_users(current_user: dict = Depends(admin_only)):
    try:
        result = supabase.table("users")\
            .select("id, name, email, role, department, created_at")\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Users fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch users"
        })

# ─── GET ALL SENIOR LECTURERS ─────────────────────────
@router.get("/senior-lecturers")
def get_senior_lecturers(current_user: dict = Depends(admin_only)):
    try:
        result = supabase.table("users")\
            .select("id, name, email, role, department, created_at")\
            .eq("role", "senior_lecturer")\
            .order("created_at", desc=True)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "Senior lecturers fetched successfully",
            "total": len(result.data),
            "data": result.data
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch senior lecturers"
        })

# ─── GET USER BY ID ───────────────────────────────────
@router.get("/users/{id}")
def get_user_by_id(id: str, current_user: dict = Depends(admin_only)):
    try:
        result = supabase.table("users")\
            .select("id, name, email, role, department, created_at")\
            .eq("id", id)\
            .execute()

        if not result.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "User not found"
            })

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "User fetched successfully",
            "data": result.data[0]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to fetch user"
        })

# ─── CREATE USER ──────────────────────────────────────
@router.post("/users")
def create_user(data: CreateUserRequest, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("users")\
            .select("id")\
            .eq("email", data.email)\
            .execute()

        if existing.data:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "User with this email already exists"
            })

        allowed_roles = ["senior_lecturer", "admin", "department_head"]
        if data.role not in allowed_roles:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": f"Invalid role. Allowed: {allowed_roles}"
            })

        if data.role == "senior_lecturer" and not data.department:
            return JSONResponse(status_code=400, content={
                "success": False,
                "message": "Department is required for senior lecturers"
            })

        hashed = hash_password(data.password)

        result = supabase.table("users").insert({
            "name": data.name,
            "email": data.email,
            "password_hash": hashed,
            "role": data.role,
            "department": data.department,
            "must_change_password": True
        }).execute()

        return JSONResponse(status_code=201, content={
            "success": True,
            "message": f"{data.role.replace('_', ' ').title()} created successfully",
            "data": {
                "id": result.data[0]["id"],
                "name": result.data[0]["name"],
                "email": result.data[0]["email"],
                "role": result.data[0]["role"],
                "department": result.data[0]["department"],
                "must_change_password": result.data[0]["must_change_password"]
            }
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to create user"
        })

# ─── UPDATE USER ──────────────────────────────────────
@router.put("/users/{id}")
def update_user(id: str, data: UpdateUserRequest, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("users")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "User not found"
            })

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}

        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))

        result = supabase.table("users")\
            .update(update_data)\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "User updated successfully",
            "data": {
                "id": result.data[0]["id"],
                "name": result.data[0]["name"],
                "email": result.data[0]["email"],
                "role": result.data[0]["role"],
                "department": result.data[0]["department"]
            }
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to update user"
        })

# ─── DELETE USER ──────────────────────────────────────
@router.delete("/users/{id}")
def delete_user(id: str, current_user: dict = Depends(admin_only)):
    try:
        existing = supabase.table("users")\
            .select("id")\
            .eq("id", id)\
            .execute()

        if not existing.data:
            return JSONResponse(status_code=404, content={
                "success": False,
                "message": "User not found"
            })

        supabase.table("users")\
            .delete()\
            .eq("id", id)\
            .execute()

        return JSONResponse(status_code=200, content={
            "success": True,
            "message": "User deleted successfully"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Failed to delete user"
        })