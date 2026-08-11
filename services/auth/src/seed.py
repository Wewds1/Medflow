"""
Database Seeding Script for MedFlow Auth Service.

This script initializes the 'db_auth' database with foundational RBAC data:
1. Permissions: Defines core system capabilities (e.g., inventory:dispense).
2. Roles: Creates roles (Admin, Doctor, Nurse, Pharmacist) and maps permissions to them.
3. Admin User: Creates a default administrator user for initial system access.

Usage:
    $env:PYTHONPATH = 'D:\Meflow\services\auth\src'
    $env:DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost:5432/db_auth'
    python services\auth\src\seed.py
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Role, Permission
from auth_utils import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def seed_db():
    async with async_session() as session:
        async with session.begin():
            # 1. Seed Permissions
            permissions_data = [
                Permission(name="inventory:dispense", description="Can dispense medication"),
                Permission(name="encounters:write", description="Can write encounter notes"),
                Permission(name="users:read", description="Can read user profiles"),
                Permission(name="admin:all", description="Full system access"),
            ]
            session.add_all(permissions_data)
            await session.flush()

            # 2. Seed Roles
            # Create Admin role with all permissions
            admin_role = Role(name="Admin")
            admin_role.permissions = permissions_data

            # Create Doctor role
            doctor_role = Role(name="Doctor")
            doctor_role.permissions = [p for p in permissions_data if p.name in ["encounters:write", "users:read"]]

            # Create Nurse role
            nurse_role = Role(name="Nurse")
            nurse_role.permissions = [p for p in permissions_data if p.name in ["users:read"]]

            # Create Pharmacist role
            pharmacist_role = Role(name="Pharmacist")
            pharmacist_role.permissions = [p for p in permissions_data if p.name in ["inventory:dispense", "users:read"]]

            session.add_all([admin_role, doctor_role, nurse_role, pharmacist_role])
            await session.flush()

            # 3. Create Default Admin User
            admin_user = User(
                username="admin",
                email="admin@medflow.local",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            admin_user.roles = [admin_role]
            session.add(admin_user)

            await session.commit()
            print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_db())
