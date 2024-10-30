# telegram_bot.py

import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.tg_user import TgUser
from database import async_session
import asyncio

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        # Регистрация команд
        self.dp.message.register(self.start_command, F.text == "/start")
        self.dp.message.register(self.help_command, F.text == "/help")
        self.dp.message.register(self.handle_message)

    async def start_command(self, message: Message):
        """Обработчик команды /start"""
        await self.add_user(message.from_user.id)
        await message.answer("Привет! Я Telegram-бот.")

    async def help_command(self, message: Message):
        """Обработчик команды /help"""
        await message.answer("Доступные команды:\n/start - начать\n/help - помощь")

    async def handle_message(self, message: Message):
        """Обработчик любого сообщения"""
        await self.add_user(message.from_user.id)

    async def add_user(self, tg_id:int):
        """Добавление пользователя в базу данных, если его нет"""
        async with async_session() as session:
            async with session.begin():
                # Проверка, есть ли пользователь в базе данных
                result = await session.execute(select(TgUser).where(TgUser.tg_id == str(tg_id)))
                user = result.scalars().first()
                if not user:
                    new_user = TgUser(tg_id=str(tg_id))
                    session.add(new_user)
                    await session.commit()

    async def send_message_to_all(self, text: str):
        """Отправка сообщения всем пользователям из базы данных"""
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(TgUser))
                user_list = result.scalars().all()

                for user in user_list:
                    try:
                        await self.bot.send_message(user.tg_id, text)
                    except Exception as e:
                        logger.error(f"Ошибка при отправке сообщения пользователю {user.tg_id}: {e}")

    async def start_polling(self):
        """Запуск long polling для Telegram-бота"""
        await self.dp.start_polling(self.bot)

# Функция для создания экземпляра бота
def create_bot(token: str) -> TelegramBot:
    return TelegramBot(token=token)
