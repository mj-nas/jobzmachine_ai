from fastapi import APIRouter, Query
from pydantic import BaseModel
from weaviate.classes.query import MetadataQuery
from app.utils.embedding_model import generate_embedding
from app.utils.weaviate import get_weaviate_client
from app.utils.upload_with_gpu import search_with_gpu
from app.utils.schema import create_resume_schema

router = APIRouter()

class JDSchema(BaseModel):
    text: str
    collection_name: str   # Default collection name


class HybridJDSchema(BaseModel):
    text: str
    collection_name: str   # Default collection name
    keyword: str 

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
    collection = client.collections.get("Resume2")
    response = collection.query.fetch_objects(
        limit= limit
    )
    client.close()
    if not response:
        return {"message": "No resumes found."}
    # print(response)
    # results = response.get("data", {}).get("Get", {})
    return {"results": response}

@router.post("/searchvector/")
async def search_resumes(body: JDSchema, limit: int = Query(..., description="Search query")):
    embedding = generate_embedding(body.text)
    client = get_weaviate_client()
    collection = client.collections.get(body.collection_name)
    if not collection:
        return {"error": "Collection not found."}

    response = collection.query.near_vector(
        near_vector=embedding,
        limit=limit,
        return_metadata=MetadataQuery(distance=True)
    )
    client.close()
    return {"query": body.text, "results": response}

@router.post("/searchvector_with_gpu/")
async def search_resumes_with_gpu(body: JDSchema, limit: int = Query(..., description="Search query")):
    
    if not body.collection_name:
        return {"error": "Collection name is required."}
    if not body.text:
        return {"error": "Search query is required."}
    response = search_with_gpu(
        query=body.text,
        collection_name=body.collection_name,
        limit=limit
    )
    return {"query": body.text, "results": response}


@router.post("/searchhybrid/")
async def search_hybrid_resumes(body: HybridJDSchema, limit: int = Query(..., description="Search query")):
    embedding = generate_embedding(body.text)
    client = get_weaviate_client()
    collection = client.collections.get(body.collection_name)
    if not collection:
        return {"error": "Collection not found."}

    response = collection.query.hybrid(
        query= body.keyword,
        vector=embedding,
        alpha=0.75,
        limit=limit,
        return_metadata=MetadataQuery(distance=True)
    )
    client.close()
    return {"query": body.text, "results": response}


