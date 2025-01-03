from typing import List
from pydantic import BaseModel, EmailStr
from sch_cart import CartBase


class UserBase(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool
    role: str = "user"
    carts: List[CartBase]
    
    class Config:
        orm_mode = True
        

class UserLogin(BaseModel):
    username: str
    password: str
  


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    
    
    class Config:
        orm_mode = True




class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

class UserUpdate(UserCreate):
    id: int
    username: str
    email: EmailStr
    password: str
    
    class config:
        orm_mode = True
        

class Admin(BaseModel):
    id:int
    name:str
    password:str