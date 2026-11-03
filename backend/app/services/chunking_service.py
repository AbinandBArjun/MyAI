import re

from app.rag.embeddings import model


MAX_MODEL_TOKENS = model.max_seq_length
TARGET_CHUNK_TOKENS = 200
CHUNK_OVERLAP = 40


def _token_count(text: str) -> int:
    """Count tokens without adding special tokens."""

    return len(
        model.tokenizer.encode(
            text,
            add_special_tokens=False,
            truncation=False,
        )
    )


def _split_oversized_word(
    word: str,
    max_tokens: int,
) -> list[str]:
    """Split a single oversized word into tokenizer-safe segments."""

    segments = []
    remaining = word

    while remaining:
        low = 1
        high = len(remaining)
        best_end = 0

        while low <= high:
            mid = (low + high) // 2

            if _token_count(remaining[:mid]) <= max_tokens:
                best_end = mid
                low = mid + 1
            else:
                high = mid - 1

        if best_end == 0:
            raise ValueError(
                "Unable to split oversized word within the token limit."
            )

        segments.append(remaining[:best_end])
        remaining = remaining[best_end:]

    return segments


def split_into_chunks(
    text: str,
    title: str = "",
) -> list[str]:
    """
    Split text into overlapping chunks using original-text word spans.

    Normal words remain intact. Oversized unbroken words are split
    into tokenizer-safe segments. Original punctuation is preserved.
    """

    if not text or not text.strip():
        return []

    tokenizer = model.tokenizer
    title = title.strip()

    special_tokens = tokenizer.num_special_tokens_to_add(pair=False)

    title_tokens = _token_count(title)

    available_content_tokens = (
        MAX_MODEL_TOKENS
        - special_tokens
        - title_tokens
        - 1
    )

    chunk_size = min(
        TARGET_CHUNK_TOKENS,
        available_content_tokens,
    )

    if chunk_size <= 0:
        raise ValueError(
            "Document title is too long to leave room for chunk content."
        )

    overlap = min(
        CHUNK_OVERLAP,
        chunk_size // 2,
    )

    # Capture words and the whitespace/punctuation between them.
    word_matches = list(re.finditer(r"\S+", text))

    if not word_matches:
        return []

    # Each unit retains its exact original character positions.
    units = []

    for match in word_matches:
        word = match.group()
        start = match.start()
        end = match.end()

        if _token_count(word) <= chunk_size:
            units.append((start, end))
        else:
            # Split only this exceptionally long unbroken word.
            segments = _split_oversized_word(word, chunk_size)

            segment_start = start

            for segment in segments:
                segment_end = segment_start + len(segment)
                units.append((segment_start, segment_end))
                segment_start = segment_end

    chunks = []
    start_index = 0

    while start_index < len(units):
        first_start = units[start_index][0]
        end_index = start_index
        best_end = first_start

        # Include original text between units, including punctuation
        # and whitespace, while respecting the token budget.
        while end_index < len(units):
            candidate_end = units[end_index][1]
            candidate = text[first_start:candidate_end]

            if _token_count(candidate) > chunk_size:
                break

            best_end = candidate_end
            end_index += 1

        if end_index == start_index:
            raise ValueError(
                "Unable to construct a chunk within the token limit."
            )

        chunk = text[first_start:best_end]

        if chunk.strip():
            chunks.append(chunk)

        if end_index >= len(units):
            break

        # Find an overlap measured using actual tokenizer tokens.
        next_start = end_index

        while next_start > start_index + 1:
            candidate_start = units[next_start - 1][0]
            overlap_text = text[candidate_start:best_end]

            if _token_count(overlap_text) > overlap:
                break

            next_start -= 1

        # Guarantee forward progress.
        if next_start <= start_index:
            next_start = end_index

        start_index = next_start

    return chunks


def build_embedding_text(
    title: str,
    chunk_content: str,
) -> str:
    """Combine title and chunk content for embedding generation."""

    title = title.strip()
    chunk_content = chunk_content.strip()

    if title:
        return f"{title}\n{chunk_content}"

    return chunk_content
