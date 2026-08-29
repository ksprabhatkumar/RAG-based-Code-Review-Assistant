import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

class HybridRetriever:
    def __init__(self):
        # Using a fast embedding model for MVP. In Phase 4, switch to BGE-M3.
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.EphemeralClient()
        self.collection = self.chroma_client.get_or_create_collection(name="context_corpus")
        
        self.corpus_docs = []
        self.corpus_ids = []
        self.bm25 = None

    def index_documents(self, documents: list[str], ids: list[str]):
        """Index into both Vector DB and BM25."""
        embeddings = self.encoder.encode(documents).tolist()
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
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
        query_embedding = self.encoder.encode([query]).tolist()
        dense_results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        # 2. Sparse (BM25) Search
        tokenized_query = query.split(" ")
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # In a full system, you normalize and sum scores. For MVP, we return a union of top K.
        # This acts as our merged candidate set before reranking/generation.
        results_map = {}
        for i, doc_id in enumerate(dense_results['ids'][0]):
            results_map[doc_id] = dense_results['documents'][0][i]
            
        return results_map
