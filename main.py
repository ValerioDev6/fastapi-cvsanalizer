import os

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.bot.bot_router import router as bot_router

router = APIRouter()

origins = [
    "http://localhost:4200",
    # "https://angular-veterinaria.onrender.com",
    # "*",
]


app = FastAPI(
    title="Api Resume IA",
    description="Api con IA Openai para vereficacion de cvs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bot_router, prefix="/api/bot", tags=["BOT CV"])
