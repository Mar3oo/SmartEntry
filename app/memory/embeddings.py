from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self):
        # lightweight + good enough
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str):
        if not text:
            return None
        return self.model.encode(text).tolist()
