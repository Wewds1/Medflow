import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(r"D:\Meflow\services\auth\.env")

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DEBUG: DATABASE_URL is {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
