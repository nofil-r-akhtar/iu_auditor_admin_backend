from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import supabase
from app.routes import auth, teachers, admin

app = FastAPI(title="IU Auditor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
def root():
    return {"message": "IU Auditor Connected"}