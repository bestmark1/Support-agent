from pydantic import BaseModel, Field


class ProposedUpdateCreate(BaseModel):
    source: str = Field(..., min_length=1)
    suggested_category: str = Field(..., pattern="^(policy|faq|product|tone)$")
    suggested_title: str = Field(..., min_length=1)
    suggested_content: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    evidence: dict[str, object] = Field(default_factory=dict)


class ProposedUpdateCreateResult(BaseModel):
    id: str = Field(..., min_length=1)
    status: str = Field(..., pattern="^(pending)$")
    created: bool = Field(...)


class ProposedUpdateReview(BaseModel):
    id: str = Field(..., min_length=1)
    action: str = Field(..., pattern="^(approve|reject|edit)$")
    reviewed_by: str = Field(..., min_length=1)
    edited_content: str | None = Field(default=None)
