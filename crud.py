from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Users, Carts
from sch_cart import CartCreate, CartBase
from sch_users import Admin, UserCreate    
from sch_product import ProductCreate

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()

 

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = Users(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def product_create(db: Session, product: ProductCreate):
    db_product = Product(name=product.name, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_by_userid(db: Session, userid: int):
    return db.query(Product).filter(Product.user_id == userid).first()  

def cart_create(db: Session, cart: CartCreate):
    db_cart = Carts(user_id=cart.user_id)  
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def get_current_users():
    return Users(id=1, username="user", email="test@example.com")
