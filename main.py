from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from nlp_engine import nlp_engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DyslexiRead API",
    description="Backend API for the DyslexiRead Chrome Extension",
    version="1.0.0"
)

# Allow CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For extension, we allow all or specific chrome-extension:// origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class TextRequest(BaseModel):
    text: str

class DifficultWord(BaseModel):
    word: str
    syllables: List[str]

class AnalysisResponse(BaseModel):
    difficult_words: List[DifficultWord]

class AnalyticsRequest(BaseModel):
    user_profile: str
    session_time_seconds: int
    words_highlighted: int

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to DyslexiRead API"}

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_text(request: TextRequest):
    """
    Analyze text to find difficult words and split them into syllables.
    """
    try:
        difficult_words = nlp_engine.analyze_text(request.text)
        return {"difficult_words": difficult_words}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics")
def track_analytics(request: AnalyticsRequest, db: Session = Depends(get_db)):
    """
    Track user reading metrics.
    """
    try:
        db_analytics = models.Analytics(
            user_profile=request.user_profile,
            session_time_seconds=request.session_time_seconds,
            words_highlighted=request.words_highlighted
        )
        db.add(db_analytics)
        db.commit()
        db.refresh(db_analytics)
        return {"status": "success", "id": db_analytics.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """
    Get aggregate analytics summary.
    """
    try:
        from sqlalchemy import func
        total_time = db.query(func.sum(models.Analytics.session_time_seconds)).scalar() or 0
        total_words = db.query(func.sum(models.Analytics.words_highlighted)).scalar() or 0
        sessions = db.query(models.Analytics).order_by(models.Analytics.created_at.desc()).limit(10).all()
        
        return {
            "total_time_minutes": round(total_time / 60, 1),
            "total_words_detected": total_words,
            "recent_sessions": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
