# routers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Cookie, HTTPException,Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session,get_async_session
from models.message import Message
from models.user import User
from .auth import get_user_by_username
from sqlalchemy.future import select
from models.token import Token
from pydantic import BaseModel 
import json
from typing import Union, Annotated
from redis_base import redis_connect


class Cookies(BaseModel):
    model_config = {"extra": "forbid"}
    auth_token:Union[str, None]

router = APIRouter()

connected_users = {}

async def send_message_history(websocket: WebSocket, session: AsyncSession):
    result = await session.execute(select(Message).order_by(Message.id))
    messages = result.scalars().all()
    for message in messages:
        await websocket.send_text(f"{message.username}: {message.content}")


async def get_user_from_token(token: str, session: AsyncSession):
    """
    Получает пользователя по токену, если он существует.

    Параметры:
        token (str): Токен, используемый для поиска пользователя.
        session (AsyncSession): Асинхронная сессия SQLAlchemy для выполнения запроса.

    Возвращает:
        User | None: Объект пользователя, если он найден; иначе None.
    """
    async def get_user_from_db(token):
        result = await session.execute(select(Token.user_id).where(Token.token == token))
        user_id = result.scalars().first()

        if user_id:
            # Ищем пользователя по user_id из токена
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            return user
    try:

        # Получаем объект токена
        cache_user = redis_connect.get(token)
        if cache_user:
            print('взял из кеша')
            return User.json_deserialize(cache_user)
        else:
            print('взял из БД')
            user = await get_user_from_db(token=token)
            redis_connect.set(token, user.json_serialize(),ex=1)
            return user
        return None
    except Exception as e:
        print(f"Ошибка при получении пользователя по токену: {e}")
        return None



@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_async_session)):
    auth_token = websocket.query_params.get('auth_token')
    print(f'auth_token: {auth_token}')
    if auth_token is None:
        await websocket.close(code=1008)
        return

    user = await get_user_from_token(auth_token, session)
    if user is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connected_users[websocket] = user.username

    # Отправка истории сообщений
    await send_message_history(websocket, session)

    try:
        while True:
            data = await websocket.receive_text()
            new_message = Message(username=user.username, content=data)
            session.add(new_message)
            await session.commit()
            for connection in connected_users:
                await connection.send_text(f"{user.username}: {data}")
    except WebSocketDisconnect:
        del connected_users[websocket]
