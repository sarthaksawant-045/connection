# indexer_service.py

from flask import Flask, request, jsonify
from query_embedder import QueryEmbedder
from indexer import index_documents
import faiss
import numpy as np
import pickle
import os

app = Flask(__name__)

# Paths
<<<<<<< HEAD
INDEX_PATH = "vector_storeAaru/index.faiss"
META_PATH = "vector_storeAaru/meta.pkl"
=======
INDEX_PATH = "vector_store/index.faiss"
META_PATH = "vector_store/meta.pkl"
>>>>>>> main

# Load embedding model once
embedder = QueryEmbedder()

def save_index(index, metadata):
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)
    print(f"✅ Saved FAISS index to {INDEX_PATH} and metadata to {META_PATH}")

def index_documents(documents: dict):
    """
    Embed and index the parsed documents using FAISS.
    
    Args:
        documents (dict): Mapping of file paths ➝ extracted text
    """
    if not documents:
        print("[INDEXER] No documents to index.")
        return

    paths = list(documents.keys())
    texts = list(documents.values())

    # Embed documents
    print(f"📊 Embedding {len(texts)} documents...")
    vectors = embedder.embed_documents(texts)

    # Normalize for cosine similarity
    faiss.normalize_L2(vectors)

    # Create FAISS index
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    # Save FAISS index and file paths
    save_index(index, paths)

@app.route("/index", methods=["POST"])
def index_api():
    try:
        data = request.get_json()
        parsed_docs = data.get("parsed_docs", {})

        print(f"[INDEXER] Received {len(parsed_docs)} documents.")
        index_documents(parsed_docs)

        return jsonify({"message": "Indexed successfully", "count": len(parsed_docs)}), 200

    except Exception as e:
        import traceback
        print("[INDEXER ERROR]", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("⚙️ Indexer Service running on port 5002")
    app.run(port=5002)
