# embedder.py

from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        print("🧠 Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Or any other model

    def embed_texts(self, texts):
        return self.model.encode(texts, convert_to_numpy=True)
