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

Answer the user's question using the retrieved knowledge context.
Be helpful, direct, and faithful to the evidence.

Rules:
1. Read the retrieved context and identify any information relevant
   to the user's question.
2. Explain relevant information in clear, natural language. The
   question does not need to use the same words as the source.
3. Explain direct implications only when they logically follow from
   the retrieved context. Distinguish reasonable inferences from
   explicitly stated facts. Never present an inference as a proven
   outcome or guarantee.
4. If the source partially answers the question, give the supported
   answer first. Then briefly state what the source does not establish.
5. For a question about benefits, risks, causes, or uses, explain
   what the source supports even if it does not provide a complete list.
   Do not claim that the source explicitly lists something when it does not.
6. Use conversation history only to understand follow-up questions.
   Use the retrieved context as evidence for factual claims.
7. Respond exactly "I could not find that information." only when
   the retrieved context contains no meaningful information relevant
   to the question.
8. Never invent personal information, facts, statistics, or details
   absent from the retrieved context.
9. Be concise. Use bullets when they improve readability.
10. Return only the answer.

Request type:
{listing_instruction}

Conversation history:
{history_text}

Retrieved knowledge context:
{context}

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

        raw_result = response.json()["response"]
        result = raw_result.strip()

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