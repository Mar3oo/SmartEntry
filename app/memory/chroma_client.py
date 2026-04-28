import chromadb


class ChromaClient:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name="documents")

    def add(self, doc_id: str, embedding, metadata: dict):
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def query(self, embedding, top_k=1):
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )
        return results
