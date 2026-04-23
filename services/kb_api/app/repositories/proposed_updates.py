import json

from sqlalchemy import text

from packages.common.db.session import get_session
from services.kb_api.app.services.language import detect_language, normalize_language


async def create_proposed_update(
    source: str,
    suggested_category: str,
    suggested_title: str,
    suggested_content: str,
    reason: str,
    evidence: dict[str, object] | None = None,
) -> tuple[str, bool]:
    async with get_session() as session:
        existing_result = await session.execute(
            text(
                """
                select id
                from proposed_updates
                where status = 'pending'
                  and suggested_category = :suggested_category
                  and suggested_title = :suggested_title
                  and suggested_content = :suggested_content
                order by created_at desc
                limit 1
                """
            ),
            {
                "suggested_category": suggested_category,
                "suggested_title": suggested_title,
                "suggested_content": suggested_content,
            },
        )
        existing_id = existing_result.scalar_one_or_none()
        if existing_id is not None:
            return str(existing_id), False

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
        return str(result.scalar_one()), True


async def review_proposed_update(
    *,
    proposed_update_id: str,
    action: str,
    reviewed_by: str,
    edited_content: str | None = None,
) -> dict[str, object]:
    async with get_session() as session:
        result = await session.execute(
            text(
                """
                select id, suggested_category, suggested_title, suggested_content, source, evidence, status
                from proposed_updates
                where id = :id
                limit 1
                """
            ),
            {"id": proposed_update_id},
        )
        row = result.mappings().first()
        if row is None:
            raise ValueError("proposed_update_not_found")

        current_status = str(row["status"] or "pending")
        if current_status != "pending":
            return {
                "id": proposed_update_id,
                "status": current_status,
                "action": action,
                "knowledge_base_id": None,
            }

        next_status = "approved" if action in {"approve", "edit"} else "rejected"
        final_content = (edited_content or "").strip() or str(row["suggested_content"] or "")
        evidence = row["evidence"] or {}
        if isinstance(evidence, str):
            try:
                evidence = json.loads(evidence)
            except Exception:
                evidence = {}
        language = normalize_language((evidence or {}).get("language")) or detect_language(final_content)

        knowledge_base_id = None
        if next_status == "approved":
            kb_result = await session.execute(
                text(
                    """
                    insert into knowledge_base (
                      category,
                      title,
                      content,
                      tags,
                      source,
                      is_approved,
                      version,
                      language,
                      canonical_key
                    )
                    values (
                      :category,
                      :title,
                      :content,
                      '{}'::text[],
                      :source,
                      true,
                      1,
                      :language,
                      null
                    )
                    returning id
                    """
                ),
                {
                    "category": row["suggested_category"],
                    "title": row["suggested_title"],
                    "content": final_content,
                    "source": f"proposed_update:{proposed_update_id}",
                    "language": language,
                },
            )
            knowledge_base_id = str(kb_result.scalar_one())

        await session.execute(
            text(
                """
                update proposed_updates
                set status = :status,
                    suggested_content = :suggested_content,
                    reviewed_at = now(),
                    reviewed_by = :reviewed_by
                where id = :id
                """
            ),
            {
                "id": proposed_update_id,
                "status": next_status,
                "suggested_content": final_content,
                "reviewed_by": reviewed_by,
            },
        )
        await session.commit()
        return {
            "id": proposed_update_id,
            "status": next_status,
            "action": action,
            "knowledge_base_id": knowledge_base_id,
        }
