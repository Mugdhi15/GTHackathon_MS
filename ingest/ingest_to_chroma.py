# ingest_to_chroma.py
import os
import chromadb
from sentence_transformers import SentenceTransformer

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE, "data", "rag_sources")

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# New client
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="rag_docs")

embed_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def ingest_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    emb = embed_model.encode([text])[0].tolist()

    collection.add(
        documents=[text],
        embeddings=[emb],
        metadatas=[{"source": filepath}],
        ids=[os.path.basename(filepath)]
    )

def run_ingestion():
    print(f"Ingesting docs from {DATA_DIR} ...")

    for file in os.listdir(DATA_DIR):
        fp = os.path.join(DATA_DIR, file)
        if fp.endswith(".txt") or fp.endswith(".md") or fp.endswith(".pdf"):
            print(" → Ingesting:", fp)
            ingest_file(fp)

    print("✓ Ingestion complete!")


if __name__ == "__main__":
    run_ingestion()
