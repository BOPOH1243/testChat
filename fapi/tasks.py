from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_async_session
from fastapi import Depends
from models.token import Token  # Импортируйте вашу модель Token
import asyncio
from models.user import User
from celery import shared_task
#from celery_app import app

@shared_task
def delete_old_tokens():
    # Запускаем асинхронный код в синхронной задаче
    asyncio.run(async_delete_old_tokens())

# tasks.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.token import Token

async def async_delete_old_tokens():
    # Извлекаем сессию из асинхронного генератора `get_async_session`
    async for session in get_async_session():
        async with session.begin():  # Начинаем транзакцию
            # Подсчёт количества токенов
            result = await session.execute(select(Token))
            tokens = result.scalars().all()
            print(tokens)
            max_tokens = 3
            
            # Если токенов больше max_tokens, удаляем лишние
            if len(tokens) > max_tokens:
                tokens_to_delete = sorted(tokens, key=lambda token: token.id)[:-max_tokens]
                print(tokens_to_delete)
                for token in tokens_to_delete:
                    await session.delete(token)
                
                await session.commit()
                print(f"Deleted {len(tokens_to_delete)} tokens.")
