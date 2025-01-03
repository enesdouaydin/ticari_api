from pydantic import BaseModel
from sch_cart import CategoryBase

class ProductBase(BaseModel):
    id: int
    name: str
    rating: int
    stock: int
    price: int
    category_id: int
    category: CategoryBase
    
    
    class Config:
        orm_mode= True


class ProductCreate(BaseModel):
    name: str
    stock: int  
    price: int
    category_id: int

    class Config:
        orm_mode = True
        
        



class ProductUpdate(ProductCreate):
    pass

class ProductAdd(BaseModel):
    pass
class ProductDelete(ProductCreate):
    mesage: str

