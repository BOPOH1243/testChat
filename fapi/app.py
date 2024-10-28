# app.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from database import init_db
from routers import auth, websocket

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Директория для шаблонов

app.include_router(auth.router, prefix="/auth")
app.include_router(websocket.router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/chat")
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
