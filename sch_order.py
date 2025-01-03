from typing import Optional
from pydantic import BaseModel

class OrderBase(BaseModel):
    id: int
    
    class Config:
        orm_mode= True
class OrderCreate(OrderBase):
    user_id: int
    cart_id: int
    class Config:
        orm_mode= True
   

class OrderUpdate(OrderBase):
    pass  
    
class OrderDelete(OrderBase):
    pass   

class OrderNotification(OrderBase):
    pass