import asyncio

from services.kb_api.app.services.backfill import (
    backfill_approved_knowledge_embeddings,
)


async def main() -> None:
    result = await backfill_approved_knowledge_embeddings()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
