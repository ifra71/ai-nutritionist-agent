from app.db.database import database


users_collection = database["users"]

conversations_collection = database["conversations"]

messages_collection = database["messages"]

food_logs_collection = database["food_logs"]

weight_records_collection = database["weight_records"]

meal_plans_collection = database["meal_plans"]