from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreate, UserUpdate
from app.db.operations import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
)


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    user_id = await create_user(user_data)

    return {
        "message": "User created successfully",
        "user_id": user_id
    }


@router.get("/{user_id}")
async def get_user(user_id: str):
    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.patch("/{user_id}")
async def edit_user(user_id: str, user_data: UserUpdate):
    updated = await update_user(user_id, user_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or no changes provided"
        )

    return {
        "message": "User updated successfully"
    }


@router.delete("/{user_id}")
async def remove_user(user_id: str):
    deleted = await delete_user(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully"
    }
