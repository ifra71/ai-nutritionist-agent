import json

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.agent.client import client
from app.agent.chat import MODEL
from app.schemas.meal_plan import MealPlanCreate
from app.db.operations import (
    create_meal_plan,
    get_user_meal_plans,
    get_user_by_id,
)


router = APIRouter(
    prefix="/api/meal-plans",
    tags=["Meal Plans"]
)


class MealPlanRequest(BaseModel):
    user_id: str = Field(min_length=1)
    daily_calories: float = Field(gt=0)
    dietary_preferences: list[str] = Field(default_factory=list)


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_meal_plan(request: MealPlanRequest):

    user = await get_user_by_id(request.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    preferences = request.dietary_preferences or user.get(
        "dietary_preferences", []
    )

    prompt = f"""
Create a practical one-day meal plan for this user.

User profile:
- Name: {user.get('name', 'User')}
- Age: {user.get('age')}
- Gender: {user.get('gender')}
- Weight: {user.get('weight_kg')} kg
- Height: {user.get('height_cm')} cm
- Goal: {user.get('goal')}
- Dietary preferences: {preferences}

Daily calorie target: {request.daily_calories} kcal.

Requirements:
- Include breakfast, lunch, dinner and at least one snack.
- Include realistic food portions in grams.
- Provide calories, protein, carbs and fat for every meal.
- Keep the total calories reasonably close to the requested target.
- Respect dietary preferences.
- Use practical, commonly available foods.
- Do not provide medical advice.

Return valid JSON only, using this exact structure:
{{
    "title": "One-Day Meal Plan",
    "daily_calories": {request.daily_calories},
    "meals": [
        {{
            "meal_type": "breakfast",
            "name": "Meal name",
            "foods": [
                {{
                    "food_name": "Food name",
                    "quantity_grams": 100
                }}
            ],
            "calories": 300,
            "protein": 15,
            "carbs": 40,
            "fat": 8
        }}
    ]
}}
"""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional AI nutritionist. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        generated_plan = json.loads(
            response.choices[0].message.content
        )

        plan_data = MealPlanCreate(
            user_id=request.user_id,
            title=generated_plan["title"],
            daily_calories=request.daily_calories,
            meals=generated_plan["meals"]
        )

        plan_id = await create_meal_plan(plan_data)

        return {
            "message": "Meal plan generated and saved successfully",
            "plan_id": plan_id,
            "meal_plan": plan_data.model_dump(mode="json")
        }

    except (ValueError, KeyError, TypeError) as error:
        raise HTTPException(
            status_code=502,
            detail=f"Could not process the generated meal plan: {str(error)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def save_meal_plan(plan_data: MealPlanCreate):

    plan_id = await create_meal_plan(plan_data)

    return {
        "message": "Meal plan saved successfully",
        "plan_id": plan_id
    }


@router.get("/{user_id}")
async def get_meal_plans(user_id: str):

    plans = await get_user_meal_plans(user_id)

    return {
        "user_id": user_id,
        "meal_plans": plans
    }
