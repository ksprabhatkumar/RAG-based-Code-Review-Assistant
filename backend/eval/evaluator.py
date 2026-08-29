import os
import json
from groq import Groq
from retrieval.indexer import HybridRetriever

class RAGEvaluator:
    def __init__(self):
        self.retriever = HybridRetriever()
        # Load same mock index for eval
        self.retriever.index_documents(
            documents=["All functions must have type hints.", "Do not hardcode API keys."],
            ids=["style_001", "sec_001"]
        )
        self.llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def eval_retrieval_recall(self, query: str, expected_chunk_id: str) -> bool:
        """Metric 1: Recall@K. Did the vector DB find the right rule?"""
        results = self.retriever.retrieve(query, top_k=3)
        return expected_chunk_id in results

    def eval_faithfulness(self, generated_explanation: str, retrieved_context: str) -> int:
        """Metric 2: LLM-as-a-judge Faithfulness. Did it hallucinate?"""
        prompt = f"""
        Does the GENERATED EXPLANATION correctly apply the rules from the RETRIEVED CONTEXT without making up new rules?
        Answer strictly with '1' for Yes (Faithful), or '0' for No (Hallucination).
        
        RETRIEVED CONTEXT: {retrieved_context}
        GENERATED EXPLANATION: {generated_explanation}
        """
        response = self.llm.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        content = response.choices[0].message.content.strip()
        print(f"DEBUG Faithfulness LLM Output: {repr(content)}")
        return 1 if "1" in content[:5] else 0

if __name__ == "__main__":
    print("Running RAG Evaluation Suite...")
    evaluator = RAGEvaluator()
    
    # Test 1: Retrieval
    query = "def calculate(a, b): return a + b"
    retrieval_pass = evaluator.eval_retrieval_recall(query, "style_001")
    print(f"Retrieval Recall@3: {'[PASS]' if retrieval_pass else '[FAIL]'}")
    
    # Test 2: Faithfulness
    context = "All functions must have type hints."
    good_explanation = "This function is missing type hints for its arguments."
    bad_explanation = "This function is missing type hints, and you should also write unit tests."
    
    score1 = evaluator.eval_faithfulness(good_explanation, context)
    score2 = evaluator.eval_faithfulness(bad_explanation, context)
    print(f"Faithfulness (Good output): {'[1.0]' if score1 == 1 else '[0.0]'}")
    print(f"Faithfulness (Hallucinated output): {'[1.0]' if score2 == 1 else '[0.0]'}")
