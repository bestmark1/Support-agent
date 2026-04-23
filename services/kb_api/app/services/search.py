from packages.common.clients.embeddings import get_embedding_client
from services.kb_api.app.repositories.knowledge import (
    fetch_approved_knowledge,
    fetch_approved_knowledge_by_vector,
)
from services.kb_api.app.services.language import normalize_language


async def search_approved_knowledge(
    query: str,
    limit: int = 5,
    language: str | None = None,
) -> list[dict[str, object]]:
    normalized_language = normalize_language(language)
    embedding_client = get_embedding_client()
    if embedding_client:
        embedding = await embedding_client.embed(query)
        vector_items = await fetch_approved_knowledge_by_vector(
            embedding=embedding,
            limit=limit,
            language=normalized_language,
        )
        if vector_items:
            return vector_items
        if normalized_language is not None:
            fallback_vector_items = await fetch_approved_knowledge_by_vector(
                embedding=embedding,
                limit=limit,
                language=None,
            )
            if fallback_vector_items:
                return fallback_vector_items

    text_items = await fetch_approved_knowledge(
        query=query,
        limit=limit,
        language=normalized_language,
    )
    if text_items:
        return text_items
    if normalized_language is not None:
        return await fetch_approved_knowledge(query=query, limit=limit, language=None)
    return text_items
