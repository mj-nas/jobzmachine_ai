from weaviate.classes.config import Configure, Property, DataType

def create_resume_schema(client, collection_name):
    try:
        if collection_name not in client.collections.list_all():
            client.collections.create(
                collection_name,
                properties=[
                    Property(name="file_id", data_type=DataType.TEXT),
                    Property(name="file_date", data_type=DataType.DATE),
                    Property(name="email", data_type=DataType.TEXT),
                    Property(name="title", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.none(),
            )
            print("✅ {collection_name} schema created using `collections` format.")
        else:
            print("ℹ️ {collection_name} schema already exists.")
    except Exception as e:
        print(f"❌ Failed to create Resume schema: {e}")