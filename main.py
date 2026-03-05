from fastapi import FastAPI
from app.config.database import supabase
from app.routes import auth

app = FastAPI(title="IU Auditor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your live domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "IU Auditor Connected"}

