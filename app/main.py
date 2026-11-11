from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import (
    connect_to_database,
    close_database_connection
)
from app.api.routes.conversations import router as conversations_router
from app.api.routes.users import router as users_router
from app.api.routes.messages import router as messages_router
from app.api.routes.food_logs import router as food_logs_router
from app.api.routes.weight_records import router as weight_router
from app.api.routes.meal_plans import router as meal_plans_router
from app.api.routes.agent import router as agent_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_database()

    yield

    await close_database_connection()


app = FastAPI(
    title="AI Nutritionist Agent",
    version="1.0.0",
    description="An AI-powered nutritionist assistant",
    lifespan=lifespan
)


app.include_router(users_router)
app.include_router(conversations_router)
app.include_router(messages_router)
app.include_router(food_logs_router)
app.include_router(weight_router)
app.include_router(meal_plans_router)
app.include_router(agent_router)

@app.get("/")
async def root():
    return {
        "message": "AI Nutritionist Agent API is running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
