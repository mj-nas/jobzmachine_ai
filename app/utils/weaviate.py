import weaviate
import os
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
print(f"WEAVIATE_URL: {WEAVIATE_URL}")


def get_weaviate_client() -> weaviate.Client:
    try:
        client = client = weaviate.connect_to_local()
        if client.is_ready():
            print("✅ Connected to Weaviate")
        else:
            print("❌ Failed to connect to Weaviate")
        return client
    except Exception as e:
        print(f"❌ Exception during Weaviate client initialization: {e}")
        raise e

def delete_weviate_collection(collection_name: str) -> None:
    """Delete a Weaviate collection."""
    client = get_weaviate_client()
    print(f"Deleting collection '{collection_name}'...")
    
    try:
        print(client.collections.list_all(simple=True).keys())
        response = client.collections.delete(collection_name)
        print(f"✅ Collection '{collection_name}' deleted successfully")
    except Exception as e:
        print(f"❌ Failed to delete collection '{collection_name}': {e}")
    
    client.close()
    return response