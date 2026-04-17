from typing import TypedDict


class KnowledgeItem(TypedDict, total=False):
    id: str
    category: str
    title: str
    content: str
    similarity: float
