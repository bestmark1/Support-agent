from packages.common.clients.embeddings import get_embedding_client
from services.kb_api.app.repositories.knowledge import (
    fetch_approved_knowledge,
    fetch_approved_knowledge_by_vector,
)


async def search_approved_knowledge(query: str, limit: int = 5) -> list[dict[str, object]]:
    embedding_client = get_embedding_client()
    if embedding_client:
        embedding = await embedding_client.embed(query)
        vector_items = await fetch_approved_knowledge_by_vector(
            embedding=embedding,
            limit=limit,
        )
        if vector_items:
            return vector_items

    return await fetch_approved_knowledge(query=query, limit=limit)
