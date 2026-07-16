import os
import httpx
from groq import Groq

def test_groq_connection(prompt: str = "Say 'Hello World'") -> str:
    """Smoke test: Call Groq API."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY not set"
    
    client = Groq(api_key=api_key)
    # Using a fast, cheap model for the smoke test
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192", 
    )
    return response.choices[0].message.content

def test_ollama_connection(prompt: str = "Say 'Hello World'") -> str:
    """Smoke test: Call local Ollama instance (assumes running on default port)."""
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b", # Or whichever code model you pulled
                "prompt": prompt,
                "stream": False
            },
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Ollama Error: {response.status_code}"
    except Exception as e:
        return f"Ollama Connection Error: {str(e)}"
