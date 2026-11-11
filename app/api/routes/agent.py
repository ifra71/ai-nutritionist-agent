from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

from app.db.database import settings
from app.agent.chat import get_ai_response
from app.tools.food_database import search_food_nutrition


router = APIRouter(
    prefix="/api/agent",
    tags=["AI Agent"]
)


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    conversation_id: str | None = None


@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        result = await get_ai_response(
            user_message=request.message,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@router.get("/search-food")
async def search_food(food_name: str):
    foods = await search_food_nutrition(food_name)

    return {
        "food_name": food_name,
        "results": foods
    }


@router.get("/debug-food/{food_id}")
async def debug_food(food_id: int):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{food_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params={"api_key": settings.USDA_API_KEY}
        )

        response.raise_for_status()
        data = response.json()

    return {
        "food_id": data.get("fdcId"),
        "food_name": data.get("description"),
        "data_type": data.get("dataType"),
        "nutrients": data.get("foodNutrients", [])[:10]
    }
