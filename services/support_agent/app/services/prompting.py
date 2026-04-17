from pathlib import Path


SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "system.md"
)


def load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def build_user_prompt(
    user_text: str,
    knowledge_items: list[dict[str, object]],
) -> str:
    knowledge_blocks: list[str] = []
    for index, item in enumerate(knowledge_items, start=1):
        title = str(item.get("title") or "Untitled")
        content = str(item.get("content") or "")
        knowledge_blocks.append(
            f"[Knowledge {index}]\nTitle: {title}\nContent: {content}"
        )

    joined_knowledge = (
        "\n\n".join(knowledge_blocks) if knowledge_blocks else "No approved knowledge found."
    )
    return (
        "User question:\n"
        f"{user_text}\n\n"
        "Approved knowledge:\n"
        f"{joined_knowledge}\n\n"
        "Answer the user using only the approved knowledge. "
        "If the knowledge is insufficient, say that the answer needs review."
    )
