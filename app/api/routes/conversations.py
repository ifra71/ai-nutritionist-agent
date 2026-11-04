from fastapi import APIRouter, HTTPException, status
from app.schemas.conversation import ConversationCreate
from app.db.operations import (
    create_conversation,
    get_conversation_by_id,
)


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def start_conversation(conversation_data: ConversationCreate):
    conversation_id = await create_conversation(conversation_data)

    return {
        "message": "Conversation created successfully",
        "conversation_id": conversation_id
    }


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    conversation = await get_conversation_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation
