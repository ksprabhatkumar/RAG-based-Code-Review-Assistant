import os
import json
from groq import Groq
from pydantic import BaseModel, Field

class ReviewComment(BaseModel):
    file: str
    line: int
    category: str = Field(description="bug, style, performance, or security")
    severity: str = Field(description="high, medium, low")
    explanation: str
    suggested_fix: str
    cited_chunk_ids: list[str] = Field(description="IDs of the context chunks that justify this review")

def generate_review(hunk: dict, expanded_code: str, context: dict) -> dict:
    """Assemble prompt, generate structured JSON, and perform grounding check."""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Format the retrieved context for the prompt
    context_str = "\n".join([f"ID: {k} | CONTENT: {v}" for k, v in context.items()])
    
    prompt = f"""
    You are an expert code reviewer. Review the code change below.
    Use ONLY the provided retrieved context to justify your review.
    If the code does not violate the context, return an empty explanation and empty citations.
    
    FILE: {hunk['file']}
    CHANGED LINE: {hunk['start_line']}
    FULL FUNCTION CONTEXT:
    {expanded_code}
    
    RETRIEVED CONTEXT:
    {context_str}
    
    Respond STRICTLY in JSON format matching this exact structure:
    {{
      "file": "{hunk['file']}",
      "line": {hunk['start_line']},
      "category": "style",
      "severity": "medium",
      "explanation": "Your explanation here based on context...",
      "suggested_fix": "code snippet here...",
      "cited_chunk_ids": ["chunk_id_1"]
    }}
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-20b", 
        response_format={"type": "json_object"}
    )
    
    raw_json = json.loads(response.choices[0].message.content)
    
    # GROUNDING CHECK (Crucial for hallucination mitigation)
    valid_citations = []
    for citation in raw_json.get("cited_chunk_ids", []):
        if citation in context:
            valid_citations.append(citation)
            
    if not valid_citations and raw_json.get("explanation"):
        # The LLM hallucinated a citation or gave an ungrounded comment.
        return {"status": "rejected", "reason": "ungrounded_hallucination", "raw": raw_json}
        
    return {"status": "success", "review": raw_json}
