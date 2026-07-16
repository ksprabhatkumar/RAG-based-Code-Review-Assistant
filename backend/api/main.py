from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="RAG Code Review Assistant - Phase 0")

@app.get("/health")
def health_check():
    """Smoke test: FastAPI app boots and returns 200."""
    return {"status": "ok", "message": "Service is running."}
