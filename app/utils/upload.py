from app.utils.weaviate import get_weaviate_client
from app.utils.embedding_model import generate_embedding
import json
from datetime import datetime
from tqdm import tqdm
from pathlib import Path


client = get_weaviate_client()


def read_json_in_batches(data, batch_size: int):
    """Yield items from the JSON in batches."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def upload_large_json_to_weaviate(json_path: str, batch_size: int):
    path = Path(json_path)
    if not path.exists() or not path.suffix == ".json":
        raise ValueError("Invalid JSON file path provided.")
    
    collection = client.collections.get("Resume2")
    
    with collection.batch.fixed_size(batch_size) as batch:
         
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            resumes = data.get("data", {}).get("resumes", [])
            if not resumes:
                raise ValueError("No resumes found in the JSON file.")
    
            print(f"Loaded {len(resumes)} resumes from {json_path}")

            total = len(resumes)
            print(f"Total resumes to upload: {total}")
            failed = 0
            progress_bar = tqdm(total=total, desc="Uploading resumes", unit="resumes")

            # for batch in read_json_in_batches(resumes, batch_size):
            #     with client.batch as batcher:
            for item in resumes:
                        try:
                            title = item.get("title", [])
                            print(f"Processing title: {title}")
                            text_for_embedding = item.get("content", [])
                            email = item.get("email")

                            if not title:
                                raise ValueError("No title provided for the resume.")

                            if not text_for_embedding:
                                raise ValueError("No text provided for embedding.")
                            
                            if not email:
                                raise ValueError("No email provided for the resume.")
                            
                            properties={
                                      "file_id": item.get("id"),
                                      "file_date": item.get("file_date", str(datetime.now())),
                                      "email": email,
                                      "title": title[0],
                                    }
                            print(f"Properties: {properties}")

                            embedding = generate_embedding(text_for_embedding[0])

                            batch.add_object(
                                properties=properties,
                                vector=embedding,
                            )

                     
                            print(f"✅ Successfully uploaded resume with ID: {item.get('id')}")
                        except Exception as e:
                            failed += 1
                            print(f"⚠️ Error processing item: {e}")
                        finally:
                            progress_bar.update(1)

            progress_bar.close()

            print(f"🎉 Finished uploading. Success: {total - failed}, Failed: {failed}")
    