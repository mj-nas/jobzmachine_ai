from sentence_transformers import SentenceTransformer
from datetime import datetime
from pathlib import Path
from app.utils.weaviate import get_weaviate_client
from app.utils.schema import create_resume_schema
import json
from tqdm import tqdm

# Load the GPU-accelerated model
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

client = get_weaviate_client()
print("device for model>>>>>>>>>>>>>>>>>>>>", model.device)  


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate vector embeddings from a list of texts using GPU."""
    if not texts:
        raise ValueError("Input text list for embedding cannot be empty.")
    
    return model.encode(
        texts,
        batch_size=32,  # Increase if GPU has enough VRAM
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()


def upload_large_json_to_weaviate_with_gpu(json_path: str, batch_size: int, collection_name: str):
    path = Path(json_path)
    if not path.exists() or not path.suffix == ".json":
        raise ValueError("Invalid JSON file path provided.")
    
    if not client.collections.exists(collection_name):
        print(f"Collection '{collection_name}' does not exist. Creating it now.")
        # Create the collection if it doesn't exist
        create_resume_schema(client, collection_name)
    
    print("Batch size (Weaviate upload):", batch_size)
    
    with client.batch.fixed_size(batch_size) as batch:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            resumes = data.get("data", {}).get("resumes", [])
            if not resumes:
                raise ValueError("No resumes found in the JSON file.")

            print(f"Loaded {len(resumes)} resumes from {json_path}")
            total = len(resumes)
            failed = 0
            counter = 0
            interval = 150  # Status log interval

            BATCH_EMBED_SIZE = 100
            buffer = []
            resume_props = []

            progress_bar = tqdm(total=total, desc="Uploading resumes", unit="resume")

            for item in resumes:
                try:
                    title = item.get("title", [])
                    content = item.get("content", [])
                    email = item.get("email") or None

                    if not title:
                        raise ValueError("No title provided for the resume.")

                    if not content:
                        raise ValueError("Missing content in resume.")

                    buffer.append(content[0])
                    resume_props.append({
                        "file_id": item.get("id"),
                        "file_date": item.get("file_date", str(datetime.now())),
                        "email": email,
                        "title": title[0],
                    })

                    if len(buffer) >= BATCH_EMBED_SIZE:
                        embeddings = generate_embeddings(buffer)

                        for props, vector in zip(resume_props, embeddings):
                            batch.add_object(
                                collection=collection_name,
                                properties=props,
                                vector=vector,
                            )
                            counter += 1
                            if counter % interval == 0:
                                print(f"✅ Imported {counter} resumes...")

                        buffer.clear()
                        resume_props.clear()

                except Exception as e:
                    failed += 1
                    print(f"⚠️ Error processing resume: {e}")
                finally:
                    progress_bar.update(1)

            # Final flush
            if buffer:
                try:
                    embeddings = generate_embeddings(buffer)
                    for props, vector in zip(resume_props, embeddings):
                        batch.add_object(
                            collection=collection_name,
                            properties=props,
                            vector=vector,
                        )
                        counter += 1
                except Exception as e:
                    failed += len(buffer)
                    print(f"⚠️ Error during final batch: {e}")

            progress_bar.close()

            failed_objects = client.batch.failed_objects
            if failed_objects:
                print(f"❌ Failed to upload {len(failed_objects)} objects.")
                for obj in failed_objects:
                    print(f"Failed object: {obj.get('email', 'Unknown')}")
            else:
                print("🎉 All objects uploaded successfully.")

            print(f"✅ Finished uploading. Success: {total - failed}, Failed: {failed}")
