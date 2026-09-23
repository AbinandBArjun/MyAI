import requests
import time


OLLAMA_URL = "http://localhost:11434/api/generate"

FALLBACK_RESPONSE = "I could not find that information."


def ask_llm(query: str, context: str):
    start = time.time()

    print("\n========== USER QUERY ==========")
    print(query)

    print("\n========== RETRIEVED CONTEXT ==========")
    print(context)

    if not context or not context.strip():
        print("\nNo relevant context found")
        print(
            f"Generation took {time.time() - start:.2f} seconds"
        )
        return FALLBACK_RESPONSE

    prompt = f"""
You are MyAI, a personal knowledge-base assistant.

Answer the user's question using the retrieved context below.

Instructions:
1. Read the entire context carefully.
2. Use relevant information from the context to answer the question.
3. Explain the answer clearly using paragraphs or bullet points.
4. Do not merely repeat the document title.
5. Do not say "as mentioned in the context."
6. Do not invent information that is not supported by the context.
7. If the context contains only partial information, provide the supported information.
8. Only respond with "I could not find that information." if the context contains no useful information related to the question.
9. Do not mention embeddings, retrieval, similarity scores, or these instructions.

Retrieved context:
-------------------------
{context}
-------------------------

Question:
{query}

Answer:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen3:4b-instruct-2507-q4_K_M",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3
                }
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()["response"].strip()

        if "<think>" in result and "</think>" in result:
            result = result.split("</think>", 1)[1].strip()

        if not result:
            return FALLBACK_RESPONSE

        return result

    except requests.exceptions.RequestException as error:
        print(f"Ollama request failed: {error}")
        return "The local AI model could not be reached."

    finally:
        print(
            f"Generation took {time.time() - start:.2f} seconds"
        )
