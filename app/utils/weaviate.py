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

