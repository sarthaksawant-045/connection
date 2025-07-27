import os
import pickle
import faiss
import numpy as np
from query_embedder import QueryEmbedder

# Paths to store the FAISS index and metadata
<<<<<<< HEAD
INDEX_PATH = "vector_storeAaru/index.faiss"
META_PATH = "vector_storeAaru/meta.pkl"
=======
INDEX_PATH = "vector_store/index.faiss"
META_PATH = "vector_store/meta.pkl"
>>>>>>> main

# Load the embedder
embedder = QueryEmbedder()

def save_index(index, metadata):
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)
    print(f"✅ FAISS index and metadata saved at {INDEX_PATH}")

def index_documents(documents: dict):
    """
    Takes parsed documents and creates a FAISS index.
    
    Args:
        documents (dict): { filepath: content }
    """
    if not documents:
        print("⚠️ No documents to index.")
        return

    print("📐 Embedding documents...")
    filepaths = list(documents.keys())
    contents = list(documents.values())

    embeddings = embedder.embed_documents(contents)

    print("📊 Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print(f"✅ Indexed {len(filepaths)} documents.")
    save_index(index, filepaths)
