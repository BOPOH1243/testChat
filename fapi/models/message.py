from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    content = Column(String)

# Настройка подключения к базе данных
DATABASE_URL = "sqlite:///./chat.db"  # SQLite
# DATABASE_URL = "postgresql://user:password@localhost/dbname"  # PostgreSQL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
