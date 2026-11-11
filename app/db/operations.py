from datetime import datetime, timezone

from bson import ObjectId

from app.db.collections import (
    users_collection,
    conversations_collection,
    messages_collection,
    food_logs_collection,
    weight_records_collection,
    meal_plans_collection,
)

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.conversation import ConversationCreate
from app.schemas.message import MessageCreate
from app.schemas.food_log import FoodLogCreate
from app.schemas.weight_record import WeightRecordCreate
from app.schemas.meal_plan import MealPlanCreate


async def create_user(user_data: UserCreate):
    result = await users_collection.insert_one(user_data.model_dump())
    return str(result.inserted_id)


async def get_user_by_id(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if user:
        user["_id"] = str(user["_id"])

    return user


async def update_user(user_id: str, user_data: UserUpdate):
    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        return False

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    return result.matched_count > 0


async def delete_user(user_id: str):
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


async def create_conversation(conversation_data: ConversationCreate):
    result = await conversations_collection.insert_one(
        conversation_data.model_dump()
    )
    return str(result.inserted_id)


async def get_conversation_by_id(conversation_id: str):
    conversation = await conversations_collection.find_one(
        {"_id": ObjectId(conversation_id)}
    )

    if conversation:
        conversation["_id"] = str(conversation["_id"])

    return conversation


async def get_user_conversations(user_id: str):
    cursor = conversations_collection.find(
        {"user_id": user_id}
    ).sort("updated_at", -1)

    conversations = await cursor.to_list(length=100)

    for conversation in conversations:
        conversation["_id"] = str(conversation["_id"])

    return conversations

async def update_conversation_timestamp(conversation_id: str):
    await conversations_collection.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"updated_at": datetime.now(timezone.utc)}}
    )


async def create_message(message_data: MessageCreate):
    result = await messages_collection.insert_one(
        message_data.model_dump()
    )
    return str(result.inserted_id)


async def get_conversation_messages(conversation_id: str):
    cursor = messages_collection.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1)

    messages = await cursor.to_list(length=100)

    for message in messages:
        message["_id"] = str(message["_id"])

    return messages


async def create_food_log(food_data: FoodLogCreate):
    result = await food_logs_collection.insert_one(
        food_data.model_dump()
    )
    return str(result.inserted_id)


async def get_user_food_logs(user_id: str):
    cursor = food_logs_collection.find(
        {"user_id": user_id}
    ).sort("logged_at", -1)

    food_logs = await cursor.to_list(length=100)

    for food in food_logs:
        food["_id"] = str(food["_id"])

    return food_logs


async def create_weight_record(weight_data: WeightRecordCreate):
    result = await weight_records_collection.insert_one(
        weight_data.model_dump()
    )
    return str(result.inserted_id)


async def get_user_weight_history(user_id: str):
    cursor = weight_records_collection.find(
        {"user_id": user_id}
    ).sort("recorded_at", 1)

    records = await cursor.to_list(length=100)

    for record in records:
        record["_id"] = str(record["_id"])

    return records


async def create_meal_plan(meal_plan_data: MealPlanCreate):
    result = await meal_plans_collection.insert_one(
        meal_plan_data.model_dump()
    )
    return str(result.inserted_id)


async def get_user_meal_plans(user_id: str):
    cursor = meal_plans_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1)

    meal_plans = await cursor.to_list(length=100)

    for plan in meal_plans:
        plan["_id"] = str(plan["_id"])

    return meal_plans
