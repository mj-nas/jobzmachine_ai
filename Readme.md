# 🔍 Resume Semantic Search API (FastAPI + Weaviate)

This project implements a semantic resume search system using **FastAPI** as the web framework and **Weaviate** as the vector database. Resumes are indexed using OpenAI embeddings, allowing you to search and retrieve the most relevant resumes based on query semantics.

---

## 🛠 Features

- Resume ingestion and vectorization using Opensource Models
- Semantic search API over 100,000+ resumes
- FastAPI backend with modular structure
- Vector DB powered by Weaviate (running locally in Docker)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/jobzmachine_ai.git
cd jobzmachine_ai

```

### 2. Setup Weaviate Database

```bash
docker compose up
```

### 3. Install Python Dependencies
Create a virtual environment (recommended) and install required packages

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

```

### 4. Start the FastAPI server
Launch the app using Uvicorn

```bash
uvicorn app.api.main:app --reload
```