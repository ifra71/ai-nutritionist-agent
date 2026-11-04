from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    user_id: str
    title: str = "New Conversation"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool = True