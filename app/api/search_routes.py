from fastapi import APIRouter, Query
from pydantic import BaseModel
from weaviate.classes.query import MetadataQuery
from app.utils.embedding_model import generate_embedding
from app.utils.weaviate import get_weaviate_client
from app.utils.schema import create_resume_schema

router = APIRouter()

class JDSchema(BaseModel):
    text: str

@router.get("/")
async def root():
    return {"message": "Welcome to the Resume Search API!"}

# collect params from the query string
# @router.get("/all?limit={limit}")
# async def get_all_resumes(limit: int = Query(5, description="Number of resumes to fetch")):

@router.get("/all/")
async def get_all_resumes(limit: int = Query(5, description="Number of resumes to fetch")):
    """
    Fetch all resumes from the Weaviate database.
    """
    client = get_weaviate_client()
    print(limit)
    collection = client.collections.get("Resume")
    client.close()
    response = collection.query.fetch_objects(
        limit= limit
    )
    if not response:
        return {"message": "No resumes found."}
    print(response)
    # results = response.get("data", {}).get("Get", {})
    return {"results": response}

@router.post("/searchvector/")
async def search_resumes(body: JDSchema, limit: int = Query(..., description="Search query")):
    embedding = generate_embedding(body.text)
    client = get_weaviate_client()
    collection = client.collections.get("Resume2")

    response = collection.query.near_vector(
        near_vector=embedding,
        limit=limit,
        return_metadata=MetadataQuery(distance=True)
    )
    client.close()
    return {"query": body.text, "results": response}
