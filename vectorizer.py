from sentence_transformers import SentenceTransformer

class Embedder:
    def _init_(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts):
        return self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)