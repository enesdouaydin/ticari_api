# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from models import Users, Carts
# from sch_cart import CartCreate
# from sch_users import UserCreate
# from database import get_db
# from auth import hashed_password

# router = APIRouter(prefix="/users", tags=["Users"])
# @router.post("/registeration")
# def register_user(user: UserCreate, db: Session = Depends(get_db)):
#     existing_user = db.query(Users).filter(Users.username == user.username).first()
    
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, 
#             detail="Kullanici adi zaten alinmiş, lütfen başka bir tane seçin."
#         )

#     hashed_pass = hashed_password(user.password)
#     db_user = Users(username=user.username,  email=user.email, hashed_password=hashed_pass) 
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)

#     return db_user


# @router.post("/cart/cart_id", status_code=201)
# def create_cart(cart: CartCreate, db: Session = Depends(get_db)):
#     get_cartt=Carts(cart=cart.cartcreate)
#     db.add(get_cartt)
#     db.commit()
#     db.refresh(get_cartt)
#     return get_cartt


# @router.post("/users/{user_id}/cart",status_code=201)
# def cart_create(cart: CartCreate, db: Session = Depends(get_db)):
#     new_cart =  Carts(cart=cart.cart_create)
#     db.add(new_cart)
#     db.commit()
    
    
#     db.refresh(new_cart)
#     return new_cart
