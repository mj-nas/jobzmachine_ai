
from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

model = SentenceTransformer("BAAI/bge-large-en-v1.5")


def generate_embedding(text: str) -> list:
    """Generate vector embedding from input text."""
    if not text:
        raise ValueError("Input text for embedding cannot be empty")
    return model.encode(text, convert_to_numpy=True).tolist()
