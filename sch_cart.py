from typing import  List
from pydantic import BaseModel
      
class CategoryBase(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode= True
    
class CategoryCreate(CategoryBase):
    name: str
    category_id: int
    class Config:
        orm_mode= True
    
class CategoryUpdate(CategoryBase):
    name: str

    
class CategoryDelete(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True

    
class CartItemBase(BaseModel):
    id: int
    cart_id: int
    product_id: int
    
    class Config:
        orm_mode= True  
    
    
    
    
class CartBase(BaseModel):
    id: int
    user_id: int
    cart_items: List[CartItemBase]
    
    class Config:
        orm_mode= True
        
            
class CartCreate(BaseModel):
    user_id: int
    cart_id: int
    
    
    class Config:
        orm_mode= True

class CartRead(CartBase):
    products: List[int]  
    pass

class CartUpdate(CartBase):
    pass

class CartDelete(CartBase):
    pass
    
    class Config:
        orm_mode = True



class CommentsBase(CartBase):
    id: int
    user_id: int
    product_id: int
    comment: str
    
    class Config:
        orm_mode= True
        

class Token(BaseModel):
    access_token: str
    token_type: str
    
