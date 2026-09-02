import chromadb
from rank_bm25 import BM25Okapi

class HybridRetriever:
    def __init__(self):
        # We removed SentenceTransformer! Chroma uses its default lightweight ONNX model automatically.
        self.chroma_client = chromadb.EphemeralClient()
        self.collection = self.chroma_client.get_or_create_collection(name="context_corpus")
        
        self.corpus_docs = []
        self.corpus_ids = []
        self.bm25 = None

    def index_documents(self, documents: list[str], ids: list[str]):
        """Index into both Vector DB and BM25."""
        # Pass the text directly. Chroma generates the embeddings behind the scenes!
        self.collection.add(
            documents=documents,
            ids=ids
        )
        self.corpus_docs.extend(documents)
        self.corpus_ids.extend(ids)
        
        # Tokenize for BM25
        tokenized_corpus = [doc.split(" ") for doc in self.corpus_docs]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 3) -> dict:
        """Hybrid search combining Vector and Keyword scores."""
        if not self.corpus_docs:
            return {}

        # 1. Dense (Vector) Search
        # Pass the raw query text instead of an embedding array
        dense_results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # 2. Sparse (BM25) Search
        tokenized_query = query.split(" ")
        if self.bm25:
            bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # In a full system, you normalize and sum scores. For MVP, we return a union of top K.
        # This acts as our merged candidate set before reranking/generation.
        results_map = {}
        if dense_results['ids'] and dense_results['ids'][0]:
            for i, doc_id in enumerate(dense_results['ids'][0]):
                results_map[doc_id] = dense_results['documents'][0][i]
                
        return results_map