from pydantic import BaseModel, Field


class SupportThreadCreate(BaseModel):
    telegram_user_id: str = Field(..., min_length=1)
    telegram_chat_id: str = Field(..., min_length=1)
    preferred_language: str | None = Field(default=None, pattern="^(ru|en)$")
    priority_support: bool = Field(default=False)
    is_test: bool = Field(default=False)


class SupportThreadStatusUpdate(BaseModel):
    thread_id: str = Field(..., min_length=1)
    case_status: str = Field(..., pattern="^(open|manual_review|resolved)$")
    resolution_note: str | None = Field(default=None)
    reviewed_by: str | None = Field(default=None)


class SupportMessageCreate(BaseModel):
    thread_id: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(user|assistant|system)$")
    message_text: str = Field(..., min_length=1)
    retrieval_context: list[dict[str, object]] = Field(default_factory=list)
    preferred_language: str | None = Field(default=None, pattern="^(ru|en)$")
