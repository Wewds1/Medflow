import asyncio
from sqlalchemy import select
from database import async_session
from models import Role

async def main():
    async with async_session() as session:
        result = await session.execute(select(Role).where(Role.name == "Doctor"))
        role = result.scalar_one_or_none()
        if role:
            print(role.id)
        else:
            print("Role not found")

if __name__ == "__main__":
    asyncio.run(main())
