from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

query = model.encode(
    "What should I learn next?"
)

note = model.encode(
    "Need to learn agents and memory"
)

similarity = cosine_similarity(
    [query],
    [note]
)

print(similarity)