from packages.common.clients.embeddings import get_embedding_client
from services.kb_api.app.repositories.knowledge import (
    fetch_approved_knowledge_without_embeddings,
    upsert_knowledge_embedding,
)


async def backfill_approved_knowledge_embeddings() -> dict[str, int]:
    embedding_client = get_embedding_client()
    if not embedding_client:
        raise RuntimeError(
            "Embedding client is not configured. Set EMBEDDING_API_KEY first."
        )

    rows = await fetch_approved_knowledge_without_embeddings()
    processed = 0

    for row in rows:
        text = "\n\n".join(filter(None, [row.get("title"), row["content"]]))
        embedding = await embedding_client.embed(text)
        await upsert_knowledge_embedding(
            knowledge_id=str(row["id"]),
            embedding=embedding,
        )
        processed += 1

    return {
        "processed": processed,
        "skipped": 0,
    }
