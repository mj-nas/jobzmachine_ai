from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from pymongo import MongoClient
import os

# Setup MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://jabir:1234@cluster0.vf1ye.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["jobzmachine_ai"]
feedback_collection = db["jobzmachine_evals"]

router = APIRouter()

# Pydantic models for validation
class RatedResume(BaseModel):
    resume_id: str
    rating: int = Field(..., ge=0, le=5)

class ResumeFeedback(BaseModel):
    job_description: str
    best_resume_id: str
    worst_resume_id: str
    best_resume_text: Optional[str] = None
    worst_resume_text: Optional[str] = None
    rated_resumes: Optional[List[RatedResume]] = [] 

@router.post("/feedback", summary="Submit user feedback on resumes")
async def submit_resume_feedback(payload: ResumeFeedback):
    try:
        feedback_doc = payload.model_dump()  # Convert Pydantic model to dict
        feedback_doc["timestamp"] = datetime.now(timezone.utc)  # Add timestamp

        result = feedback_collection.insert_one(feedback_doc)

        return {"message": "✅ Feedback submitted successfully", "id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to store feedback: {e}")
