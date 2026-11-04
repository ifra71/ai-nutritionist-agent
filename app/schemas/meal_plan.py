from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MealPlanCreate(BaseModel):
    user_id: str
    title: str
    daily_calories: float = Field(gt=0)
    meals: list[dict]
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )