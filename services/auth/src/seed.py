"""
Database Seeding Script for MedFlow Auth Service.

This script initializes the 'db_auth' database with comprehensive RBAC data
covering all 7 bounded contexts of the MedFlow Ecosystem.

Usage:
    $env:PYTHONPATH = 'D:\Meflow\services\auth\src'
    python services\auth\src\seed.py
"""
import asyncio
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from database import Base
from models import User, Role, Permission
from auth_utils import get_password_hash

# Load environment variables from the service's .env file
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
            # 1. Define Comprehensive Permissions for the 7 Bounded Contexts
            permissions_map = {
                # Auth & RBAC
                "auth:manage": "Manage users, roles, and permissions",
                "users:read": "Read user profiles",

                # Appointments
                "appts:read": "View appointment schedules",
                "appts:write": "Create or modify appointments",

                # EHR & Encounters
                "ehr:read": "View patient clinical records",
                "ehr:write": "Create or modify encounter notes",

                # Triage & Risk
                "triage:read": "View triage scores and alerts",
                "triage:write": "Record vitals and NEWS2 scores",

                # Pharmacy & Stock
                "pharmacy:read": "View medication history",
                "pharmacy:dispense": "Dispense medication from stock",
                "pharmacy:inventory": "Manage medication inventory",

                # Lab System (LIS)
                "lis:read": "View lab results",
                "lis:order": "Order lab tests",

                # Billing & RCM
                "billing:read": "View invoices and claims",
                "billing:write": "Create or modify invoices",
            }

            permissions = [Permission(name=k, description=v) for k, v in permissions_map.items()]
            session.add_all(permissions)
            await session.flush()

            # Helper to get permission objects by name
            def get_perms(names):
                return [p for p in permissions if p.name in names]

            # 2. Define Roles and map them to permissions
            roles_data = [
                {
                    "name": "Admin",
                    "perms": list(permissions_map.keys())
                },
                {
                    "name": "Doctor",
                    "perms": [
                        "appts:read", "ehr:read", "ehr:write",
                        "triage:read", "lis:read", "lis:order", "pharmacy:read"
                    ]
                },
                {
                    "name": "Nurse",
                    "perms": [
                        "appts:read", "triage:write", "triage:read",
                        "ehr:read", "lis:order"
                    ]
                },
                {
                    "name": "Pharmacist",
                    "perms": [
                        "pharmacy:dispense", "pharmacy:inventory",
                        "pharmacy:read", "ehr:read"
                    ]
                },
                {
                    "name": "BillingClerk",
                    "perms": [
                        "billing:read", "billing:write", "appts:read", "users:read"
                    ]
                },
                {
                    "name": "FrontDesk",
                    "perms": [
                        "appts:read", "appts:write", "users:read"
                    ]
                },
            ]

            roles = []
            for rd in roles_data:
                role = Role(name=rd["name"])
                role.permissions = get_perms(rd["perms"])
                roles.append(role)

            session.add_all(roles)
            await session.flush()

            # 3. Create Default Admin User
            # We check if the user exists first to allow re-running the script
            result = await session.execute(select(User).where(User.username == "admin"))
            if not result.scalar_one_or_none():
                admin_user = User(
                    username="admin",
                    email="admin@medflow.local",
                    hashed_password=get_password_hash("admin123"),
                    is_active=True
                )
                # Assign the Admin role
                admin_role = next(r for r in roles if r.name == "Admin")
                admin_user.roles = [admin_role]
                session.add(admin_user)
                print("Default admin user created.")
            else:
                print("Admin user already exists, skipping creation.")

            await session.commit()
            print("Database seeded successfully with comprehensive RBAC data!")

if __name__ == "__main__":
    asyncio.run(seed_db())
