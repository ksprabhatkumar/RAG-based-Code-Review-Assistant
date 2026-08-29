import os
from groq import Groq

llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))

retrieved_context = "All functions must have type hints."
generated_explanation = "This function is missing type hints for its arguments."

prompt = f"""
Given the RETRIEVED CONTEXT, does the GENERATED EXPLANATION contain only facts supported by the context?
Answer strictly with '1' for Yes (Faithful), or '0' for No (Hallucination).

RETRIEVED CONTEXT: {retrieved_context}
GENERATED EXPLANATION: {generated_explanation}
"""

response = llm.chat.completions.create(
    messages=[{"role": "user", "content": prompt}],
    model="llama-3.1-8b-instant"
)
print("Raw response:", repr(response.choices[0].message.content))
