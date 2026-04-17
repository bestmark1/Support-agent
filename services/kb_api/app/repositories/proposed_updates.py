import json

from sqlalchemy import text

from packages.common.db.session import get_session


async def create_proposed_update(
    source: str,
    suggested_category: str,
    suggested_title: str,
    suggested_content: str,
    reason: str,
    evidence: dict[str, object] | None = None,
) -> str:
    async with get_session() as session:
        sql = text(
            """
            insert into proposed_updates (
              source,
              suggested_category,
              suggested_title,
              suggested_content,
              reason,
              evidence
            )
            values (
              :source,
              :suggested_category,
              :suggested_title,
              :suggested_content,
              :reason,
              cast(:evidence as jsonb)
            )
            returning id
            """
        )
        result = await session.execute(
            sql,
            {
                "source": source,
                "suggested_category": suggested_category,
                "suggested_title": suggested_title,
                "suggested_content": suggested_content,
                "reason": reason,
                "evidence": json.dumps(evidence or {}),
            },
        )
        await session.commit()
        return str(result.scalar_one())
