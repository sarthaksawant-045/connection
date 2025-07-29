# ✅ indexer.py
import os
import pickle
import faiss
from embedder import Embedder

INDEX_PATH = "Aaryan_store/index.faiss"
META_PATH = "Aaryan_store/meta.pkl"

embedder = Embedder()

def index_documents(documents: dict):
    texts = [v["content"] if v["content"] else v["filename"] for v in documents.values()]
    metadata = list(documents.values())

    print(f"🧠 Starting embedding for {len(texts)} documents...")
    vectors = embedder.embed_texts(texts)
    print("✅ Embedding complete.")

    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(documents, f)

    print(f"✅ FAISS index saved to '{INDEX_PATH}'. Total documents indexed: {len(documents)}")
