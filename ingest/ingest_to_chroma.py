# ingest_to_chroma.py
import os, json
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from tqdm import tqdm
import glob

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR","./chroma_db")

def load_texts_from_pdf(path):
    text = ""
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    return text

def main():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_DIR))
    collection = client.get_or_create_collection("rag_docs")

    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    docs = []
    metadatas = []
    ids = []

    # ingest text files and PDFs
    files = glob.glob("../data/rag_sources/*")
    for i, fpath in enumerate(files):
        text = load_texts_from_pdf(fpath)
        chunks = []
        # naive chunking
        chunk_size = 500
        for j in range(0, max(1,len(text)), chunk_size):
            chunk = text[j:j+chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        for idx, chunk in enumerate(chunks):
            docs.append(chunk)
            metadatas.append({"source":os.path.basename(fpath)})
            ids.append(f"{os.path.basename(fpath)}_{idx}")

    # also ingest JSON data like offers/inventory as small docs
    for jsonfile in ["../data/offers.json","../data/inventory.json","../data/customers.json"]:
        try:
            with open(jsonfile) as f:
                text = f.read()
            docs.append(text)
            metadatas.append({"source":os.path.basename(jsonfile)})
            ids.append(os.path.basename(jsonfile))
        except:
            pass

    # embed using the same model
    embeddings = model.encode(docs, show_progress_bar=True).tolist()
    # upsert into chroma
    collection.add(ids=ids, documents=docs, metadatas=metadatas, embeddings=embeddings)
    client.persist()
    print("Ingested", len(docs), "documents to Chroma at", CHROMA_DIR)

if __name__ == "__main__":
    main()
