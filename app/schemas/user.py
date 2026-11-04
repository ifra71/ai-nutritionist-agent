from pydantic import BaseModel, Field
from typing import Literal

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int
    gender: str | None = None
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    goal: Literal["weight_loss", "muscle_gain", "maintenance"]
    dietary_preferences: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    age: int | None = None
    gender: str | None = None
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    goal: Literal["weight_loss", "muscle_gain", "maintenance"] | None = None
    dietary_preferences: list[str] | None = None
