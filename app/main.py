from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import (
    connect_to_database,
    close_database_connection
)


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