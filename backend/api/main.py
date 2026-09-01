from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.webhook import router as webhook_router
from api.database import SessionLocal, ReviewLog
import os

app = FastAPI(title="RAG Code Review Assistant")

# Allow Next.js frontend to fetch data
# In production, set CORS_ORIGINS to your Vercel URL (e.g. https://rag-reviewer.vercel.app)
origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running."}

@app.get("/api/reviews")
def get_reviews(db: Session = Depends(get_db)):
    """Fetch all reviews for the dashboard."""
    reviews = db.query(ReviewLog).order_by(ReviewLog.id.desc()).all()
    return reviews
