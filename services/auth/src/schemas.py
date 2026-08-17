from pydantic import BaseModel, EmailStr
from typing import List, Optional

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    permission_ids: List[int]

class Role(RoleBase):
    id: int
    permissions: List[Permission] = []
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    roles: List[Role] = []
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    permissions: List[str] = []

class RoleAssignment(BaseModel):
    role_id: int

class LoginRequest(BaseModel):
    username: str
    password: str


