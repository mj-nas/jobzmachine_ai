from fastapi import APIRouter
from fastapi import Request, Form
import os
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.utils.upload import  upload_large_json_to_weaviate

router = APIRouter()

class UploadRequest(BaseModel):
    json_path: str  # Local path to your JSON file

@router.get("/")
async def root():
    return {"message": "Welcome to the Resume Upload API!"}


@router.post("/json")
async def upload_from_json(request: UploadRequest):
    """Upload resume data from a JSON file on disk."""
    if not os.path.isfile(request.json_path):
        return JSONResponse(content={"error": "Invalid file path"}, status_code=400)
    
    try:
        upload_large_json_to_weaviate(request.json_path, 2)
        return {"message": "Resumes uploaded successfully from JSON"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    