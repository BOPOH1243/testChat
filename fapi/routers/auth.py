# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from database import get_async_session  # изменим вызов зависимости для сессии
from models.user import User
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from models.token import Token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

async def get_user_by_username(session: AsyncSession, username: str):
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/register")
async def register(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    db_user = await get_user_by_username(session, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    return {"msg": "User registered successfully"}

@router.post("/login")
async def login(user_data: UserLogin, response: Response, session: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_username(session, user_data.username)
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Создаем токен и сохраняем в базе
    token = Token(user_id=user.id)
    session.add(token)
    await session.commit()

    # Отправляем токен в куки
    response.set_cookie(key="auth_token", value=token.token, max_age=60*60*24*7)  # Токен на 7 дней
    return {"message": "Logged in successfully"}
