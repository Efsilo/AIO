from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List

# User schemas
class UserRegister(BaseModel):
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Advertisement schemas
class AdvertisementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)

class AdvertisementResponse(BaseModel):
    id: str
    title: str
    description: str
    price: float
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True