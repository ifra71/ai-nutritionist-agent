from datetime import datetime, timezone

from pydantic import BaseModel, Field


class WeightRecordCreate(BaseModel):
    user_id: str
    weight_kg: float = Field(gt=0)
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )