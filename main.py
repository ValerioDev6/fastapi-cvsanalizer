import os

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse

from apps.bot.bot_router import router as bot_router

router = APIRouter()


app = FastAPI(
    title="Api Resume IA",
    description="Api con IA Openai para vereficacion de cvs",
    version="1.0.0",
)


app.include_router(bot_router, prefix="/bot", tags=["BOT CV"])
