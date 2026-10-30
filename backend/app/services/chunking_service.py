from app.rag.embeddings import model


MAX_MODEL_TOKENS = model.max_seq_length
TARGET_CHUNK_TOKENS = 200
CHUNK_OVERLAP = 40


def split_into_chunks(
    text: str,
    title: str = ""
) -> list[str]:
    """
    Split document content into overlapping chunks.

    Reserve token space for the title and special tokens
    so the combined embedding input stays within the
    embedding model's maximum sequence length.
    """

    if not text or not text.strip():
        return []

    tokenizer = model.tokenizer

    title = title.strip()

    # Account for special tokens added by the model.
    special_tokens = tokenizer.num_special_tokens_to_add(
        pair=False
    )

    # Reserve space for title and its separator.
    title_token_count = len(
        tokenizer.encode(
            title,
            add_special_tokens=False
        )
    )

    available_content_tokens = (
        MAX_MODEL_TOKENS
        - special_tokens
        - title_token_count
        - 1
    )

    chunk_size = min(
        TARGET_CHUNK_TOKENS,
        available_content_tokens
    )

    if chunk_size <= 0:
        raise ValueError(
            "Document title is too long to leave room for chunk content."
        )

    overlap = min(
        CHUNK_OVERLAP,
        chunk_size // 2
    )

    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False
    )

    if not token_ids:
        return []

    chunks = []
    start = 0

    while start < len(token_ids):
        end = min(
            start + chunk_size,
            len(token_ids)
        )

        chunk_token_ids = token_ids[start:end]

        chunk_text = tokenizer.decode(
            chunk_token_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        ).strip()

        if chunk_text:
            chunks.append(chunk_text)

        if end >= len(token_ids):
            break

        start = end - overlap

    return chunks


def build_embedding_text(
    title: str,
    chunk_content: str
) -> str:
    """
    Combine the document title and chunk content
    for embedding generation.
    """

    title = title.strip()
    chunk_content = chunk_content.strip()

    if title:
        return f"{title}\n{chunk_content}"

    return chunk_content
