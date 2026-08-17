"""
Database Seeding Script for MedFlow Auth Service.

This script initializes the 'db_auth' database with comprehensive RBAC data
covering all 7 bounded contexts of the MedFlow Ecosystem.
"""
import asyncio
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from dotenv import load_dotenv

from database import Base
from models import User, Role, Permission
from auth_utils import get_password_hash

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in .env file")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def seed_db():
    async with async_session() as session:
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session.begin():
            # 1. Define Comprehensive Permissions
            permissions_map = {
                "auth:manage": "Manage users, roles, and permissions",
                "users:read": "Read user profiles",
                "appts:read": "View appointment schedules",
                "appts:write": "Create or modify appointments",
                "ehr:read": "View patient clinical records",
                "ehr:write": "Create or modify encounter notes",
                "triage:read": "View triage scores and alerts",
                "triage:write": "Record vitals and NEWS2 scores",
                "pharmacy:read": "View medication history",
                "pharmacy:dispense": "Dispense medication from stock",
                "pharmacy:inventory": "Manage medication inventory",
                "lis:read": "View lab results",
                "lis:order": "Order lab tests",
                "billing:read": "View invoices and claims",
                "billing:write": "Create or modify invoices",
            }

            # Upsert Permissions
            permissions_objs = {}
            for name, desc in permissions_map.items():
                res = await session.execute(select(Permission).where(Permission.name == name))
                perm = res.scalar_one_or_none()
                if not perm:
                    perm = Permission(name=name, description=desc)
                    session.add(perm)
                permissions_objs[name] = perm

            await session.flush()

            # 2. Define Roles and map them to permissions
            roles_data = [
                {"name": "Admin", "perms": list(permissions_map.keys())},
                {"name": "Doctor", "perms": ["appts:read", "ehr:read", "ehr:write", "triage:read", "lis:read", "lis:order", "pharmacy:read"]},
                {"name": "Nurse", "perms": ["appts:read", "triage:write", "triage:read", "ehr:read", "lis:order"]},
                {"name": "Pharmacist", "perms": ["pharmacy:dispense", "pharmacy:inventory", "pharmacy:read", "ehr:read"]},
                {"name": "BillingClerk", "perms": ["billing:read", "billing:write", "appts:read", "users:read"]},
                {"name": "FrontDesk", "perms": ["appts:read", "appts:write", "users:read"]},
            ]

            roles_objs = {}
            for rd in roles_data:
                res = await session.execute(
                    select(Role).where(Role.name == rd["name"]).options(selectinload(Role.permissions))
                )
                role = res.scalar_one_or_none()
                if not role:
                    role = Role(name=rd["name"])
                    session.add(role)

                # Sync permissions for the role
                target_perms = [permissions_objs[p_name] for p_name in rd["perms"]]
                role.permissions = target_perms
                roles_objs[rd["name"]] = role

            await session.flush()

            # 3. Create Default Admin User
            result = await session.execute(
                select(User).where(User.username == "admin").options(selectinload(User.roles))
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                admin_user = User(
                    username="admin",
                    email="admin@medflow.local",
                    hashed_password=get_password_hash("admin123"),
                    is_active=True
                )
                session.add(admin_user)

            # Ensure admin has Admin role
            admin_role = roles_objs["Admin"]
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)

            await session.commit()
            print("Database seeded successfully with idempotent RBAC data!")

if __name__ == "__main__":
    asyncio.run(seed_db())
