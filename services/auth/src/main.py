from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .database import get_db
from .models import User, Role, Permission
from .schemas import UserCreate, UserOut, Token
from .auth_utils import get_password_hash, create_access_token, verify_password


app = FastAPI(title="MedFlow Auth Service")

@app.get("/")
async def root():
    return {"message": "Auth Service is running"}

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
    await db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login(user_credentials: UserCreate, db: AsyncSession = Depends(get_db)):
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

