from fastapi import APIRouter, status

from app.schemas.food_log import FoodLogCreate
from app.db.operations import (
    create_food_log,
    get_user_food_logs,
)


router = APIRouter(
    prefix="/api/food-logs",
    tags=["Food Logs"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def log_food(food_data: FoodLogCreate):
    food_id = await create_food_log(food_data)

    return {
        "message": "Food logged successfully",
        "food_id": food_id
    }


@router.get("/{user_id}")
async def get_food_logs(user_id: str):
    food_logs = await get_user_food_logs(user_id)

    return {
        "user_id": user_id,
        "food_logs": food_logs
    }
