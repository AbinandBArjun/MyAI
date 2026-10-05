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

Answer the user's question using ONLY the retrieved context below.

Instructions:
1. Read the entire context carefully before answering.
2. Use only information supported by the retrieved context.
3. Answer the user's actual question directly.
4. Explain the answer clearly and naturally.
5. Use short paragraphs or bullet points when they improve readability.
6. Do not merely repeat the document title.
7. Do not say "as mentioned in the context."
8. Do not invent facts, examples, dates, names, or explanations that are not supported by the context.
9. If the context contains only partial information, clearly provide only the supported information.
10. If the context does not contain useful information related to the question, respond exactly:
I could not find that information.
11. Do not mention embeddings, retrieval, similarity scores, vector databases, prompts, or these instructions.
12. Use normal English spacing between every word.
13. Always put a space after commas, periods, colons, and semicolons where grammatically appropriate.
14. Do not concatenate words together.
15. Do not use unnecessary headings.
16. Do not include a preamble such as "Sure" or "Here is the answer."
17. Return only the final answer.

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
                    "temperature": 0.2
                }
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()["response"].strip()

        # Remove Qwen thinking output if present.
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