from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .models import User, Role, Permission
from .schemas import UserCreate, UserOut, Token
from .auth_utils import get_password_hash, create_access_token

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
    # Simplified login check
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.username == user_credentials.username))
    db_user = result.scalar_one_or_none()
    
    if not db_user or not (db_user.hashed_password == user_credentials.password): # Should use verify_password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract permissions for the token
    permissions = [] 
    
    access_token = create_access_token(
        data={"sub": db_user.username, "permissions": permissions}
    )
    return {"access_token": access_token, "token_type": "bearer"}
