from pydantic import BaseModel, Field


class SupportThreadCreate(BaseModel):
    telegram_user_id: str = Field(..., min_length=1)
    telegram_chat_id: str = Field(..., min_length=1)


class SupportMessageCreate(BaseModel):
    thread_id: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(user|assistant|system)$")
    message_text: str = Field(..., min_length=1)
    retrieval_context: list[dict[str, object]] = Field(default_factory=list)
