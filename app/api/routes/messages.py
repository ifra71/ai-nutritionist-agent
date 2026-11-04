from fastapi import APIRouter, HTTPException, status
from app.schemas.message import MessageCreate
from app.db.operations import (
    create_message,
    get_conversation_messages,
    get_conversation_by_id,
)


router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def send_message(message_data: MessageCreate):
    conversation = await get_conversation_by_id(
        message_data.conversation_id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    message_id = await create_message(message_data)

    return {
        "message": "Message saved successfully",
        "message_id": message_id
    }


@router.get("/{conversation_id}")
async def get_messages(conversation_id: str):
    conversation = await get_conversation_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = await get_conversation_messages(conversation_id)

    return {
        "conversation_id": conversation_id,
        "messages": messages
    }
