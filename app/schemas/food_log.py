from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class FoodLogCreate(BaseModel):
    user_id: str
    food_name: str
    quantity: float = Field(gt=0)
    serving_unit: str
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)
    meal_type: Literal[
        "breakfast",
        "lunch",
        "dinner",
        "snack"
    ]
    logged_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )