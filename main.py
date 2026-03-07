from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ← this line was missing!
from app.config.database import supabase
from app.routes import auth, teachers

app = FastAPI(title="IU Auditor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])  # ← add this

@app.get("/")
def root():
    return {"message": "IU Auditor Connected"}