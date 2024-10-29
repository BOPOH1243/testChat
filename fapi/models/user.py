# models/user.py
from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship
import json

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    tokens = relationship("Token", back_populates="user")

    def json_serialize(self):
        return json.dumps({
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password
        })
    
    @staticmethod
    def json_deserialize(json_str):
        data = json.loads(json_str)
        return User(id=data.get("id"), username=data.get("username"), hashed_password=data.get("hashed_password"))