from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from models.message import Message, Base

app = FastAPI()

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Асинхронное подключение к базе данных
DATABASE_URL = "sqlite+aiosqlite:///./chat.db"  # SQLite
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"  # PostgreSQL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Создание базы данных и таблицы
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_db()

# Хранилище активных WebSocket-соединений и никнеймов
connected_users = {}

# Jinja2 для рендеринга HTML шаблонов
env = Environment(loader=FileSystemLoader("templates"))

# Генерация простого HTML-интерфейса
@app.get("/")
async def get():
    template = env.get_template("index.html")
    return HTMLResponse(template.render())

# Обработчик WebSocket-соединений
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Присвоение никнейма пользователю
    user_id = f"user{len(connected_users) + 1}"
    await websocket.accept()
    connected_users[websocket] = user_id

    # Отправка истории сообщений при подключении
    await send_message_history(websocket)

    await notify_users(f"{user_id} присоединился к чату.")

    try:
        while True:
            # Получение сообщения от пользователя
            data = await websocket.receive_text()
            await save_message(user_id, data)  # Сохранение сообщения в БД
            await notify_users(f"{user_id}: {data}")
    except WebSocketDisconnect:
        # Обработка отключения
        del connected_users[websocket]
        await notify_users(f"{user_id} покинул чат.")

# Функция для отправки сообщений всем подключенным пользователям
async def notify_users(message: str):
    for connection in connected_users:
        await connection.send_text(message)

# Функция для отправки истории сообщений
async def send_message_history(websocket: WebSocket):
    async with async_session() as session:
        # Используем текстовый запрос
        result = await session.execute(text("SELECT username, content FROM messages"))
        messages = result.fetchall()  # Получаем все результаты
        
        for msg in messages:
            await websocket.send_text(f"{msg[0]}: {msg[1]}")  # msg[0] - username, msg[1] - content

# Асинхронная функция для сохранения сообщения в БД
async def save_message(username: str, content: str):
    async with async_session() as session:
        async with session.begin():
            new_message = Message(username=username, content=content)
            session.add(new_message)
