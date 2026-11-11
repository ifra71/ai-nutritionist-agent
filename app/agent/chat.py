import json

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.agent.client import client
from app.tools.nutrition import calculate_nutrition
from app.tools.food_database import search_food_nutrition
from app.schemas.food_log import FoodLogCreate
from app.schemas.weight_record import WeightRecordCreate
from app.schemas.conversation import ConversationCreate
from app.schemas.message import MessageCreate
from app.schemas.user import UserUpdate
from app.db.operations import (
    create_food_log,
    get_user_food_logs,
    create_weight_record,
    get_user_weight_history,
    create_conversation,
    get_conversation_by_id,
    create_message,
    get_conversation_messages,
    update_conversation_timestamp,
    get_user_by_id,
    update_user
)


MODEL = "openai/gpt-oss-120b"
PAKISTAN_TZ = ZoneInfo("Asia/Karachi")


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_food_nutrition",
            "description": "Search USDA FoodData Central for nutrition values per 100g, including calories, macros, vitamins and minerals. Use before calculating nutrition for food.",
            "parameters": {
                "type": "object",
                "properties": {
                    "food_name": {"type": "string"}
                },
                "required": ["food_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_nutrition",
            "description": "Calculate calories, macros, vitamins and minerals for a food quantity in grams using USDA values per 100g.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quantity_grams": {"type": "number"},
                    "calories_per_100g": {"type": "number"},
                    "protein_per_100g": {"type": "number"},
                    "carbs_per_100g": {"type": "number"},
                    "fat_per_100g": {"type": "number"},
                    "additional_nutrients_per_100g": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number"},
                                "unit": {"type": "string"}
                            },
                            "required": ["amount", "unit"]
                        }
                    }
                },
                "required": [
                    "quantity_grams",
                    "calories_per_100g",
                    "protein_per_100g",
                    "carbs_per_100g",
                    "fat_per_100g"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_food_log",
            "description": "Save food the user has eaten or explicitly asks to log. First search USDA and calculate nutrition. Do not save future meals or hypothetical foods.",
            "parameters": {
                "type": "object",
                "properties": {
                    "food_name": {"type": "string"},
                    "quantity_grams": {"type": "number"},
                    "calories": {"type": "number"},
                    "protein": {"type": "number"},
                    "carbs": {"type": "number"},
                    "fat": {"type": "number"},
                    "meal_type": {
                        "type": "string",
                        "enum": ["breakfast", "lunch", "dinner", "snack"]
                    }
                },
                "required": [
                    "food_name",
                    "quantity_grams",
                    "calories",
                    "protein",
                    "carbs",
                    "fat",
                    "meal_type"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_food_logs",
            "description": "Retrieve saved food logs for questions about today's meals, calories or food history.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_weight_record",
            "description": "Save a new weight record when the user reports a new measurement or explicitly asks to record their weight.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number"}
                },
                "required": ["weight_kg"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weight_history",
            "description": "Retrieve all saved weight records, including first, previous and current weight.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_user_profile",
            "description": "Update the user's saved profile when they explicitly ask to save, update or correct their personal information. Only include fields the user wants changed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "gender": {"type": "string"},
                    "height_cm": {"type": "number"},
                    "weight_kg": {"type": "number"},
                    "goal": {
                        "type": "string",
                        "enum": ["weight_loss", "muscle_gain", "maintenance"]
                    },
                    "dietary_preferences": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": []
            }
        }
    }
]


SYSTEM_PROMPT = """
You are an AI Nutritionist Assistant.

GENERAL:

- Answer exactly what the user asks.
- Be concise and direct.
- Prefer 1-3 short sentences.
- Do not add unrelated information.
- Use only tools needed for the request.
- Never claim an action succeeded unless the tool confirms it.
- The application supplies the user's ID. Never generate or change it.

USER PROFILE:

- Use the supplied saved profile when relevant.
- Respect the user's dietary preferences.
- Do not assume allergies or medical conditions.
- For current weight, prefer the latest saved weight tracking record over profile weight.

PROFILE UPDATES:

- When the user explicitly asks to update, correct or save profile information, call update_user_profile.
- Save only the fields the user provides or explicitly asks to change.
- Never overwrite fields the user has not mentioned.
- When the user explicitly updates their current weight, update the profile and create a new weight history record.
- Do not update the profile just because the user asks a general question.
- Confirm profile updates only after the database operation succeeds.

FOOD NUTRITION:

- Search USDA FoodData Central before providing nutrition values.
- Select the closest matching food and preparation method.
- If the user asks only for calories, provide calories only.
- If the user asks for macros, provide calories, protein, carbs and fat.
- If the user asks about vitamins, minerals or fiber, use the additional nutrients returned by USDA.
- When calculating micronutrients, pass the selected food's nutrients_per_100g into additional_nutrients_per_100g.
- Give values per 100g when quantity is not specified.
- If a quantity is specified, calculate nutrition for that quantity.
- Never invent nutrition values.
- Never assume a missing nutrient has a value of zero.
- Mention when USDA does not provide a requested nutrient value.
- Preserve the units returned by USDA.

FOOD LOGGING:

- When the user says they ate, had, consumed or finished eating a food, treat it as a food diary entry and save it.
- Also save when the user explicitly asks to log or record food.
- Do not save hypothetical foods, future meals or general nutrition questions.
- Search USDA, calculate nutrition, then call save_food_log.
- Use the actual quantity in grams when provided.
- For common count-based portions, a reasonable standard estimate may be used. Tell the user when the quantity is estimated.
- If the amount cannot reasonably be estimated, ask the user.
- Identify the meal from the user's message.
- If the meal is unclear, ask whether it was breakfast, lunch, dinner or snack.
- Log multiple foods separately.
- Confirm logging only after saving succeeds.

FOOD HISTORY:

- For questions about today's food, call get_food_logs.
- Use food_logs_today for today's food.
- Use daily_summary for today's totals.
- Use all_food_logs for previous history.
- Only report foods present in saved records.

WEIGHT TRACKING:

- Save a new weight record whenever the user reports a new measurement or asks to record their weight.
- Never delete previous records.
- Use current_weight_kg for current weight.
- Use first_record for oldest recorded weight.
- Use previous_weight_kg for previous weight.
- Use weight_history for complete history.
- Never guess weight values.
- Do not save weight during general weight-loss advice.
"""


async def get_ai_response(
    user_message: str,
    user_id: str,
    conversation_id: str | None = None
):
    user_profile = await get_user_by_id(user_id)

    if user_profile:
        profile_context = f"""
USER PROFILE:
- Name: {user_profile.get("name")}
- Age: {user_profile.get("age")}
- Gender: {user_profile.get("gender")}
- Height: {user_profile.get("height_cm")} cm
- Profile weight: {user_profile.get("weight_kg")} kg
- Goal: {user_profile.get("goal")}
- Dietary preferences: {user_profile.get("dietary_preferences", [])}

Use this profile when relevant.
For current weight, prefer saved weight tracking records over profile weight.
"""
    else:
        profile_context = "No user profile is available."

    if conversation_id is None:
        conversation_data = ConversationCreate(
            user_id=user_id,
            title=user_message[:60]
        )
        conversation_id = await create_conversation(conversation_data)
    else:
        conversation = await get_conversation_by_id(conversation_id)

        if not conversation or conversation.get("user_id") != user_id:
            raise ValueError("Conversation not found for this user.")

    await create_message(
        MessageCreate(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
    )

    previous_messages = await get_conversation_messages(conversation_id)

    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT + "\n\n" + profile_context
    }]

    for message in previous_messages:
        if message["role"] in ("user", "assistant"):
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })

    for _ in range(5):
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            answer = assistant_message.content or ""

            await create_message(
                MessageCreate(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=answer
                )
            )

            await update_conversation_timestamp(conversation_id)

            return {
                "response": answer,
                "conversation_id": conversation_id
            }

        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "search_food_nutrition":
                result = await search_food_nutrition(**arguments)

            elif function_name == "calculate_nutrition":
                result = calculate_nutrition(**arguments)

            elif function_name == "save_food_log":
                food_data = FoodLogCreate(
                    user_id=user_id,
                    food_name=arguments["food_name"],
                    quantity=arguments["quantity_grams"],
                    serving_unit="g",
                    calories=arguments["calories"],
                    protein=arguments["protein"],
                    carbs=arguments["carbs"],
                    fat=arguments["fat"],
                    meal_type=arguments["meal_type"]
                )

                food_id = await create_food_log(food_data)

                result = {
                    "success": True,
                    "food_log_id": food_id,
                    "food_name": arguments["food_name"],
                    "quantity_grams": arguments["quantity_grams"],
                    "meal_type": arguments["meal_type"]
                }

            elif function_name == "get_food_logs":
                records = await get_user_food_logs(user_id)
                today = datetime.now(PAKISTAN_TZ).date()
                today_records = []

                for record in records:
                    logged_at = record.get("logged_at")

                    if isinstance(logged_at, str):
                        logged_at = datetime.fromisoformat(
                            logged_at.replace("Z", "+00:00")
                        )

                    if not isinstance(logged_at, datetime):
                        continue

                    if logged_at.tzinfo is None:
                        logged_at = logged_at.replace(tzinfo=timezone.utc)

                    local_date = logged_at.astimezone(PAKISTAN_TZ).date()

                    if local_date == today:
                        today_records.append(record)

                daily_summary = {
                    "calories": round(
                        sum(float(r.get("calories", 0)) for r in today_records), 2
                    ),
                    "protein": round(
                        sum(float(r.get("protein", 0)) for r in today_records), 2
                    ),
                    "carbs": round(
                        sum(float(r.get("carbs", 0)) for r in today_records), 2
                    ),
                    "fat": round(
                        sum(float(r.get("fat", 0)) for r in today_records), 2
                    )
                }

                result = {
                    "date": today.isoformat(),
                    "total_records_today": len(today_records),
                    "food_logs_today": today_records,
                    "daily_summary": daily_summary,
                    "all_food_logs": records
                }

            elif function_name == "save_weight_record":
                weight_data = WeightRecordCreate(
                    user_id=user_id,
                    weight_kg=arguments["weight_kg"]
                )

                record_id = await create_weight_record(weight_data)

                result = {
                    "success": True,
                    "record_id": record_id,
                    "weight_kg": arguments["weight_kg"]
                }

            elif function_name == "get_weight_history":
                records = await get_user_weight_history(user_id)

                result = {
                    "total_records": len(records),
                    "first_record": records[0] if records else None,
                    "previous_weight_kg": (
                        records[-2]["weight_kg"] if len(records) >= 2 else None
                    ),
                    "current_weight_kg": (
                        records[-1]["weight_kg"] if records else None
                    ),
                    "weight_history": records
                }

            elif function_name == "update_user_profile":
                if not arguments:
                    result = {
                        "success": False,
                        "error": "No profile fields were provided."
                    }
                else:
                    profile_data = UserUpdate(**arguments)
                    success = await update_user(user_id, profile_data)

                    weight_record_id = None

                    if success and "weight_kg" in arguments:
                        weight_data = WeightRecordCreate(
                            user_id=user_id,
                            weight_kg=arguments["weight_kg"]
                        )

                        weight_record_id = await create_weight_record(weight_data)

                    result = {
                        "success": success,
                        "updated_fields": list(arguments.keys()),
                        "weight_record_id": weight_record_id
                    }

            else:
                result = {"error": "Unknown tool"}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, default=str)
            })

    answer = "I couldn't complete your request. Please try again."

    await create_message(
        MessageCreate(
            conversation_id=conversation_id,
            role="assistant",
            content=answer
        )
    )

    await update_conversation_timestamp(conversation_id)

    return {
        "response": answer,
        "conversation_id": conversation_id
    }
