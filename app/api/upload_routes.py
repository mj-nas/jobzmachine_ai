from fastapi import APIRouter
from fastapi import Request, Form
import os
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.utils.upload import  upload_large_json_to_weaviate

router = APIRouter()

class UploadRequest(BaseModel):
    json_path: str  # Local path to your JSON file
    collection_name: str  # Name of the Weaviate collection
    batch_size: int   # Default batch size for uploading

@router.get("/")
async def root():
    return {"message": "Welcome to the Resume Upload API!"}


@router.post("/json")
async def upload_from_json(request: UploadRequest):
    """Upload resume data from a JSON file on disk."""
    if not os.path.isfile(request.json_path):
        return JSONResponse(content={"error": "Invalid file path"}, status_code=400)
    
    # check if the collection name is valid
    if not request.collection_name:
        return JSONResponse(content={"error": "Collection name is required"}, status_code=400)
    
    # check if the batch size is valid
    if request.batch_size <= 0:
        return JSONResponse(content={"error": "Batch size must be greater than 0"}, status_code=400)
    
    try:
        upload_large_json_to_weaviate(request.json_path, request.batch_size, request.collection_name)
        
        return {"message": "Resumes uploaded successfully from JSON"}
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    