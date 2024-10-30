# models/tg_user.py
from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship
import json

class TgUser(Base):
    __tablename__ = "tg_users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String, nullable=True)