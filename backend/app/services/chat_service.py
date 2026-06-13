import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_llm(query: str, context: str):
    start = time.time()

    prompt = f"""
You are Mypedia.

Answer ONLY using the provided context.

If the answer is not found in the context, say:
"I could not find that information."

Keep answers short and direct.

Context:
{context}

Question:
{query}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3:4b",
            "prompt": prompt,
            "stream": False
        }
    )

    print(
        f"Generation took {time.time() - start:.2f} seconds"
    )

    return response.json()["response"]