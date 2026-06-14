from app.rag.embeddings import get_embedding

embedding = get_embedding(
    "LangChain helps build AI agents."
)

print(type(embedding))
print(len(embedding))