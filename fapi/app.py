# app.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from database import init_db
from routers import auth, websocket
import asyncio
from telegram_bot import create_bot
from database import get_async_session
from sqlalchemy.event import listens_for
from models.message import Message
from database import Base, async_session

tg_token = '7950989453:AAHRsPWrOU4CYWj03muFb4g4WpNS5fp1qWE'

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Директория для шаблонов

app.include_router(auth.router, prefix="/auth")
app.include_router(websocket.router)

@app.on_event("startup")
async def startup_event():
    await init_db()

# Создаем экземпляр TelegramBot
telegram_bot = create_bot(tg_token)

@app.on_event("startup")
async def on_startup():
    """Запуск бота при старте FastAPI-приложения"""
    asyncio.create_task(telegram_bot.start_polling())
    #await telegram_bot.send_message_to_all('блять')


@app.get("/chat")
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@listens_for(Message, "after_insert")
def after_insert_message(mapper, connection, target):
    """Обработчик события после вставки нового сообщения"""
    text = f"Пользователь {target.username} отправил сообщение: {target.content}"
    print(text)
    # Создаем фоновую задачу для асинхронной отправки сообщений
    asyncio.create_task(telegram_bot.send_message_to_all(text))