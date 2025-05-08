from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.upload_routes import router as upload_router
from app.api.search_routes import router as search_router
from app.utils.weaviate import get_weaviate_client
from app.utils.schema import create_resume_schema
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Weaviate client and schema on startup
    client = get_weaviate_client()
    create_resume_schema(client)
    app.state.weaviate = client
    
    yield

    # 🔒 Shutdown: close Weaviate client
    client.close()
    print("🔌 Weaviate client closed")

# Initialize FastAPI app with CORS middleware
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Create FastAPI app instance

# Include the routes for uploading and searching
app.include_router(upload_router, prefix="/upload", tags=["upload"])
app.include_router(search_router, prefix="/search", tags=["search"])

# Root endpoint (optional)
@app.get("/")
async def root():
    return {"message": "Welcome to the Resume Search API!"}
