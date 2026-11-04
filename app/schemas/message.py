from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    conversation_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )