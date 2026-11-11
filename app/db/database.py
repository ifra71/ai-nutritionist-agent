from pymongo import AsyncMongoClient
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    MONGODB_URL: str
    DATABASE_NAME: str
    GROQ_API_KEY: str
    USDA_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()

client = AsyncMongoClient(settings.MONGODB_URL)

database = client[settings.DATABASE_NAME]


async def connect_to_database():
    await client.admin.command("ping")
    print("MongoDB connection successful")


async def close_database_connection():
    await client.close()