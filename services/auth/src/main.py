from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .database import get_db
from .models import User, Role, Permission
from .schemas import UserCreate, UserOut, Token, RoleAssignment, LoginRequest
from .auth_utils import get_password_hash, create_access_token, verify_password, decode_access_token
import os
from typing import List, Annotated
from jose import JWTError

app = FastAPI(title="MedFlow Auth Service")

# Load Public Key for token verification
PUBLIC_KEY_PATH = os.getenv("RSA_PUBLIC_KEY_PATH", "public.pem")
try:
    with open(PUBLIC_KEY_PATH, "rb") as f:
        PUBLIC_KEY = f.read()
except FileNotFoundError:
    PUBLIC_KEY = None

async def get_current_user(authorization: Annotated[str | None, Header()] = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header",
        )

    token = authorization.split(" ")[1]
    if PUBLIC_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Public key not loaded on server",
        )

    payload = decode_access_token(token, PUBLIC_KEY)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, user: Annotated[dict, Depends(get_current_user)]):
        permissions = user.get("permissions", [])
        if self.required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.required_permission}",
            )
        return user

@app.get("/")
async def root():
    return {"message": "Auth Service is running"}

@app.post("/users/{user_id}/roles", status_code=status.HTTP_200_OK)
async def assign_role(
    user_id: int,
    assignment: RoleAssignment,
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("auth:manage"))
):
    # Fetch user and role
    user_result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.roles))
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role_result = await db.execute(select(Role).where(Role.id == assignment.role_id))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role in user.roles:
        return {"message": f"User already has the role {role.name}"}

    user.roles.append(role)
    await db.commit()
    return {"message": f"Role {role.name} assigned to user {user.username}"}

@app.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_200_OK)
async def remove_role(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(PermissionChecker("auth:manage"))
):
    # Fetch user and role
    user_result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.roles))
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role not in user.roles:
        raise HTTPException(status_code=400, detail="User does not have this role")

    user.roles.remove(role)
    await db.commit()
    return {"message": f"Role {role.name} removed from user {user.username}"}

@app.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )
    db.add(db_user)
    await db.commit()

    # Fetch the user again with roles loaded to avoid MissingGreenlet in response serialization
    result = await db.execute(
        select(User)
        .where(User.id == db_user.id)
        .options(selectinload(User.roles))
    )
    return result.scalar_one()

@app.post("/token", response_model=Token)
async def login(user_credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Fetch user with roles and permissions using selectinload to avoid N+1 queries
    result = await db.execute(
        select(User)
        .where(User.username == user_credentials.username)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user_credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract unique permissions for the token
    permissions = list(set(p.name for role in db_user.roles for p in role.permissions))

    access_token = create_access_token(
        data={"sub": db_user.username, "permissions": permissions}
    )
    return {"access_token": access_token, "token_type": "bearer"}

