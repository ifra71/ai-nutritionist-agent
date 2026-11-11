from fastapi import APIRouter, status
from app.schemas.weight_record import WeightRecordCreate
from app.db.operations import (
    create_weight_record,
    get_user_weight_history,
)


router = APIRouter(
    prefix="/api/weight",
    tags=["Weight Tracking"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def record_weight(weight_data: WeightRecordCreate):
    record_id = await create_weight_record(weight_data)

    return {
        "message": "Weight recorded successfully",
        "record_id": record_id
    }


@router.get("/{user_id}")
async def get_weight_history(user_id: str):
    records = await get_user_weight_history(user_id)

    return {
        "user_id": user_id,
        "weight_history": records
    }
