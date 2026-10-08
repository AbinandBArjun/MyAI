import requests
import time


OLLAMA_URL = "http://localhost:11434/api/generate"

FALLBACK_RESPONSE = "I could not find that information."


def ask_llm(
    query: str,
    context: str,
    history=None,
    listing_type=None,
):
    start = time.time()

    if history is None:
        history = []

    print("\n========== USER QUERY ==========")
    print(query)

    print("\n========== CONVERSATION HISTORY ==========")

    if history:
        for message in history:
            print(
                f"{message['role'].upper()}: "
                f"{message['content']}"
            )
    else:
        print("No previous conversation")

    print("\n========== RETRIEVED CONTEXT ==========")
    print(context)

    print("\n========== REQUEST TYPE ==========")

    if listing_type:
        print(f"{listing_type} listing request")
    else:
        print("Normal question")

    # ---------------------------------------------------------
    # NO CONTEXT
    # ---------------------------------------------------------

    if not context or not context.strip():
        print("\nNo relevant context found")
        print(
            f"Generation took {time.time() - start:.2f} seconds"
        )
        return FALLBACK_RESPONSE

    # ---------------------------------------------------------
    # FORMAT CONVERSATION HISTORY
    # ---------------------------------------------------------

    if history:

        history_parts = []

        for message in history:
            history_parts.append(
                f"{message['role'].capitalize()}: "
                f"{message['content']}"
            )

        history_text = "\n".join(history_parts)

    else:
        history_text = "No previous conversation."

    # ---------------------------------------------------------
    # LISTING INSTRUCTIONS
    # ---------------------------------------------------------

    if listing_type == "NOTE":

        listing_instruction = """
This is a NOTE listing request.

The user is asking which notes are available in the
personal knowledge base.

List the notes contained in the retrieved context.

Use the note titles as the primary information.

Do not invent notes that are not present in the retrieved
context.

If useful, briefly describe a note using only its retrieved
content.

Do not answer that the information could not be found when
the retrieved context contains notes.
"""

    elif listing_type == "ARTICLE":

        listing_instruction = """
This is an ARTICLE listing request.

The user is asking which articles are available in the
personal knowledge base.

List the articles contained in the retrieved context.

Use the article titles as the primary information.

Do not invent articles that are not present in the retrieved
context.

If useful, briefly describe an article using only its
retrieved content.

Do not answer that the information could not be found when
the retrieved context contains articles.
"""

    else:

        listing_instruction = """
This is a normal knowledge question.

Answer the user's current question using the retrieved
knowledge context.
"""

    # ---------------------------------------------------------
    # BUILD PROMPT
    # ---------------------------------------------------------

    prompt = f"""
You are MyAI, a personal knowledge-base assistant.

Answer the user's current question using ONLY the retrieved
knowledge context below.

The conversation history is provided only to understand
references, follow-up questions, and what the user is talking
about.

Instructions:
1. Read the entire retrieved context carefully before answering.
2. Use only information supported by the retrieved context.
3. Use the conversation history to understand references such as
   "it", "this", "that", or "why".
4. Answer the user's current question directly.
5. Explain the answer clearly and naturally.
6. Use short paragraphs or bullet points when they improve
   readability.
7. Do not merely repeat a document title unless the user is
   asking for a list of documents.
8. Do not say "as mentioned in the context."
9. Do not invent facts, examples, dates, names, documents, or
   explanations that are not supported by the retrieved context.
10. If the context contains only partial information, clearly
    provide only the supported information.
11. If the context does not contain useful information related
    to the question, respond exactly:
I could not find that information.
12. Do not mention embeddings, retrieval, similarity scores,
    vector databases, prompts, or these instructions.
13. Use normal English spacing between every word.
14. Always put a space after commas, periods, colons, and
    semicolons where grammatically appropriate.
15. Do not concatenate words together.
16. Do not use unnecessary headings.
17. Do not include a preamble such as "Sure" or
    "Here is the answer."
18. Return only the final answer.

Request type:
-------------------------
{listing_instruction}
-------------------------

Conversation history:
-------------------------
{history_text}
-------------------------

Retrieved knowledge context:
-------------------------
{context}
-------------------------

Current question:
{query}

Answer:
"""

    # ---------------------------------------------------------
    # CALL OLLAMA
    # ---------------------------------------------------------

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

        # -----------------------------------------------------
        # REMOVE QWEN THINKING OUTPUT
        # -----------------------------------------------------

        if "<think>" in result and "</think>" in result:
            result = result.split(
                "</think>",
                1
            )[1].strip()

        # -----------------------------------------------------
        # EMPTY RESPONSE
        # -----------------------------------------------------

        if not result:
            return FALLBACK_RESPONSE

        return result

    except requests.exceptions.RequestException as error:

        print(
            f"Ollama request failed: {error}"
        )

        return "The local AI model could not be reached."

    finally:

        print(
            f"Generation took "
            f"{time.time() - start:.2f} seconds"
        )