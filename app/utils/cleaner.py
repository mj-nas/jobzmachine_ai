import re

def preprocess_resume_text(text: str) -> str:
    # Remove multiple newlines and replace with single space
    cleaned = re.sub(r"\n+", " ", text)
    # Remove extra spaces
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    return cleaned