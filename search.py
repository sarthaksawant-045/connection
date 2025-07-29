import faiss
import pickle
import numpy as np

INDEX_PATH = "Aaryan_store/index.faiss"
META_PATH = "Aaryan_store/meta.pkl"

def search_documents(query: str, embedder, top_k=5):
    # ✅ Step 1: Embed the query
    query_embedding = embedder.embed_texts([query])
    faiss.normalize_L2(query_embedding)

    # ✅ Step 2: Load FAISS index
    index = faiss.read_index(INDEX_PATH)

    # ✅ Step 3: Load metadata (paths)
    with open(META_PATH, "rb") as f:
        all_paths = pickle.load(f)

    # ✅ Step 4: Perform search
    D, I = index.search(query_embedding, top_k)

    results = []
    for idx in I[0]:
        if idx < len(all_paths):
            path = all_paths[idx]
            results.append({
                "filename": path.split("\\")[-1],
                "path": path,
                "extension": "." + path.split(".")[-1],
                "modified": "",  # Optional: Add os.path.getmtime(path)
            })

    return results
