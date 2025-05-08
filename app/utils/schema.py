import weaviate.classes.config as wc

def create_resume_schema(client):
    try:
        if "Resume2" not in client.collections.list_all():
            client.collections.create(
                name="Resume2",
                properties=[
                    wc.Property(name="file_id", data_type=wc.DataType.TEXT),
                    wc.Property(name="file_date", data_type=wc.DataType.DATE),
                    wc.Property(name="email", data_type=wc.DataType.TEXT),
                    wc.Property(name="title", data_type=wc.DataType.TEXT),
                ],
                vectorizer_config=wc.Configure.Vectorizer.none(),
            )
            print("✅ 'Resume2' schema created using `collections` format.")
        else:
            print("ℹ️ 'Resume2' schema already exists.")
    except Exception as e:
        print(f"❌ Failed to create Resume schema: {e}")