from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

app = FastAPI()

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    await notify_users(f"{user_id} присоединился к чату.")

    try:
        while True:
            # Получение сообщения от пользователя
            data = await websocket.receive_text()
            await notify_users(f"{user_id}: {data}")
    except WebSocketDisconnect:
        # Обработка отключения
        del connected_users[websocket]
        await notify_users(f"{user_id} покинул чат.")

# Функция для отправки сообщений всем подключенным пользователям
async def notify_users(message: str):
    for connection in connected_users:
        await connection.send_text(message)
