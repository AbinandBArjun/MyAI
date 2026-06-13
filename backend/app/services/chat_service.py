import requests
import time

def ask_llm(prompt: str):
    start = time.time()

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:4b",
            "prompt": prompt,
            "stream": False
        }
    )

    print(f"Generation took {time.time() - start:.2f} seconds")

    return response.json()["response"]

OLLAMA_URL = "http://localhost:11434/api/generate"


