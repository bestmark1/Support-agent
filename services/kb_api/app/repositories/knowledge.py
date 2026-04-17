from sqlalchemy import text

from packages.common.db.session import get_session


async def fetch_approved_knowledge(query: str, limit: int) -> list[dict[str, object]]:
    async with get_session() as session:
        sql = text(
            """
            select id, category, title, content
            from knowledge_base
            where is_approved = true
              and (
                coalesce(title, '') ilike :needle
                or content ilike :needle
              )
            order by updated_at desc
            limit :limit
            """
        )
        result = await session.execute(
            sql,
            {"needle": f"%{query}%", "limit": limit},
        )
        return [dict(row._mapping) for row in result]


async def fetch_approved_knowledge_by_vector(
    embedding: list[float],
    limit: int,
) -> list[dict[str, object]]:
    async with get_session() as session:
        sql = text(
            """
            select
              kb.id,
              kb.category,
              kb.title,
              kb.content,
              1 - (ke.embedding <=> cast(:embedding as vector)) as similarity
            from knowledge_embeddings ke
            join knowledge_base kb on kb.id = ke.knowledge_id
            where kb.is_approved = true
            order by ke.embedding <=> cast(:embedding as vector)
            limit :limit
            """
        )
        result = await session.execute(
            sql,
            {"embedding": str(embedding), "limit": limit},
        )
        return [dict(row._mapping) for row in result]


async def fetch_approved_knowledge_without_embeddings() -> list[dict[str, object]]:
    async with get_session() as session:
        sql = text(
            """
            select kb.id, kb.title, kb.content
            from knowledge_base kb
            left join knowledge_embeddings ke on ke.knowledge_id = kb.id
            where kb.is_approved = true
              and ke.knowledge_id is null
            order by kb.created_at asc
            """
        )
        result = await session.execute(sql)
        return [dict(row._mapping) for row in result]


async def upsert_knowledge_embedding(
    knowledge_id: str,
    embedding: list[float],
) -> None:
    async with get_session() as session:
        sql = text(
            """
            insert into knowledge_embeddings (knowledge_id, embedding)
            values (:knowledge_id, cast(:embedding as vector))
            on conflict (knowledge_id)
            do update set embedding = excluded.embedding
            """
        )
        await session.execute(
            sql,
            {
                "knowledge_id": knowledge_id,
                "embedding": str(embedding),
            },
        )
        await session.commit()
