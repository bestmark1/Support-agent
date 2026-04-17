from pydantic import BaseModel, Field


class ProposedUpdateCreate(BaseModel):
    source: str = Field(..., min_length=1)
    suggested_category: str = Field(..., pattern="^(policy|faq|product|tone)$")
    suggested_title: str = Field(..., min_length=1)
    suggested_content: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    evidence: dict[str, object] = Field(default_factory=dict)
