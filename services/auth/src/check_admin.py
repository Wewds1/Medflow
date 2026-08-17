import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import async_session
from models import User, Role

async def main():
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == "admin").options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        if user:
            print(f"User: {user.username}")
            print(f"Roles: {[role.name for role in user.roles]}")
            for role in user.roles:
                # Load permissions for each role
                res = await session.execute(
                    select(Role).where(Role.id == role.id).options(selectinload(Role.permissions))
                )
                role_with_perms = res.scalar_one()
                print(f"Role {role_with_perms.name} permissions: {[p.name for p in role_with_perms.permissions]}")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    asyncio.run(main())
