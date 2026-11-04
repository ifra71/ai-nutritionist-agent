from app.db.collections import users_collection
from app.schemas.user import UserCreate, UserUpdate
from bson import ObjectId
from app.db.collections import conversations_collection
from app.schemas.conversation import ConversationCreate
from app.db.collections import messages_collection
from app.schemas.message import MessageCreate
from app.db.collections import food_logs_collection
from app.schemas.food_log import FoodLogCreate
from app.db.collections import weight_records_collection
from app.schemas.weight_record import WeightRecordCreate
from app.db.collections import meal_plans_collection
from app.schemas.meal_plan import MealPlanCreate

async def create_user(user_data: UserCreate):
    user_document = user_data.model_dump()

    result = await users_collection.insert_one(user_document)

    return str(result.inserted_id)


async def get_user_by_id(user_id: str):
    user = await users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )

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
    result = await users_collection.delete_one(
        {"_id": ObjectId(user_id)}
    )

    return result.deleted_count > 0


async def create_conversation(conversation_data: ConversationCreate):
    conversation_document = conversation_data.model_dump()

    result = await conversations_collection.insert_one(
        conversation_document
    )

    return str(result.inserted_id)


async def get_conversation_by_id(conversation_id: str):
    conversation = await conversations_collection.find_one(
        {"_id": ObjectId(conversation_id)}
    )

    if conversation:
        conversation["_id"] = str(conversation["_id"])

    return conversation


async def create_message(message_data: MessageCreate):
    message_document = message_data.model_dump()

    result = await messages_collection.insert_one(message_document)

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
    food_document = food_data.model_dump()

    result = await food_logs_collection.insert_one(food_document)

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
    weight_document = weight_data.model_dump()

    result = await weight_records_collection.insert_one(weight_document)

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
    meal_plan_document = meal_plan_data.model_dump()

    result = await meal_plans_collection.insert_one(
        meal_plan_document
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