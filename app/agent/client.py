from groq import AsyncGroq
from app.db.database import settings


client = AsyncGroq(
    api_key=settings.GROQ_API_KEY
)