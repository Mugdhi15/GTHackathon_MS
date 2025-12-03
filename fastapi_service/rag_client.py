# rag_client.py
import os
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# New Chroma client format (IMPORTANT)
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection("rag_docs")

embed_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def query_rag(query, top_k=3):
    q_emb = embed_model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents","metadatas","distances"]
    )

    docs = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        docs.append({
            "text": doc,
            "meta": meta,
            "dist": dist
        })

    return docs
