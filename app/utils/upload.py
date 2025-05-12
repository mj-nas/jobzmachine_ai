from app.utils.weaviate import get_weaviate_client
from app.utils.embedding_model import generate_embedding
from app.utils.schema import create_resume_schema
import json
from datetime import datetime
from tqdm import tqdm
from pathlib import Path


client = get_weaviate_client()


def read_json_in_batches(data, batch_size: int):
    """Yield items from the JSON in batches."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def upload_large_json_to_weaviate(json_path: str, batch_size: int, collection_name: str):
    path = Path(json_path)
    if not path.exists() or not path.suffix == ".json":
        raise ValueError("Invalid JSON file path provided.")
    
    create_resume_schema(client, collection_name)
    
    print("batch size: ", batch_size)
    
    with client.batch.fixed_size(batch_size) as batch:
         
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


            counter = 0
            interval = 150  # Print status every 100 resumes
            # for batch in read_json_in_batches(resumes, batch_size):
            #     with client.batch as batcher:
            for item in resumes:
                        try:
                            title = item.get("title", [])
                            file_path = item.get("file_path", [])
                            if not file_path:
                                raise ValueError("No file path provided for the resume.")
                            print(f"Processing title: {title}")
                            text_for_embedding = item.get("content", [])
                            email = item.get("email") or None

                            if not title:
                                raise ValueError("No title provided for the resume.")

                            if not text_for_embedding:
                                raise ValueError("No text provided for embedding.")
                            
                            
                            properties={
                                      "file_id": item.get("id"),
                                      "file_path": file_path[0],
                                      "file_date": item.get("file_date", str(datetime.now())),
                                      "email": email,
                                      "title": title[0],
                                    }
                            print(f"Properties: {properties}")

                            embedding = generate_embedding(text_for_embedding[0])

                            batch.add_object(
                                collection=collection_name,
                                properties=properties,
                                vector=embedding,
                            )

                            counter += 1
                            if counter % interval == 0:
                                print(f"Imported ✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅{counter} articles...")


                     
                            print(f"✅ Successfully uploaded resume with ID: {item.get('id')}")
                        except Exception as e:
                            failed += 1
                            print(f"⚠️ Error processing item: {e}")
                        finally:
                            progress_bar.update(1)

            progress_bar.close()
            failed_objects = client.batch.failed_objects
            if failed_objects:
                print(f"Failed to upload {len(failed_objects)} objects.")
                for obj in failed_objects:
                    print(f"Failed object: {obj.get('email', 'Unknown')}")
            else:
                print("All objects uploaded successfully.")
            # Close the batch to ensure all objects are sent

            # client.close()

            print(f"🎉 Finished uploading. Success: {total - failed}, Failed: {failed}")
    