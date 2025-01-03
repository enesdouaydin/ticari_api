import json
import secrets
from tkinter import Image
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, UploadFile, WebSocket, WebSocketDisconnect, status, File, Query
from fastapi.security import OAuth2PasswordRequestForm
from auth import hashed_password, get_current_admin
from passlib.context import CryptContext
from crud import  verify_password

from database import Base, engine, get_db
from sch_product import ProductCreate
from sqlalchemy.orm import Session 
from models import Category, Users, Carts, Product, CartItem, Comment,Order
from auth import authenticate_user, create_access_token
from sch_cart import CartCreate, CartDelete, CategoryCreate, CommentsBase, Token
from sch_order import  OrderCreate
from sch_users import UserLogin, UserCreate, UserResponse, UserUpdate
from PIL import Image

from websocket import ConnectionManager


Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



app = FastAPI()







@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Geçersiz kullanici adi veya şifre")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/registeration")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.username == user.username).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Kullanici adi zaten alinmiş, lütfen başka bir tane seçin."
        )

    hashed_pass = hashed_password(user.password)
    db_user = Users(username=user.username,  email=user.email, hashed_password=hashed_pass) 
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, UserLogin.username, UserLogin.password)
    if not authenticated_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token(data={"sub": authenticated_user.username})
    return {"access_token": access_token, "token_type": "bearer"}



# @app.post("/users/", status_code=201)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     hash_pass = hashed_password(user.hashed_password)
#     user.password = hash_pass  
#     new_user = Users(username=user.username, password=user.password, role=user.role)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


@app.post("/user/{users_id}/cart/{cart_id}", status_code=201) 
def create_cart(users_id: int, cart: CartCreate, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == users_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="kullanici bulunamadi")
    
    existing_cart = db.query(Carts).filter(Carts.user_id == users_id).first()

    if existing_cart:
        raise HTTPException(status_code=401, detail="kullanici zaten bir sepete sahip")

    new_cart = Carts(user_id=users_id,cart_id=cart.cart_id)
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    
    return new_cart



@app.get("/user/{users_id}/cart")
def get_cart(users_id: int, db: Session = Depends(get_db)):
    cart = db.query(Carts).filter(Carts.user_id == users_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="cart bulunamadi")
    return cart



@app.delete("/user/{users_id}/cart",status_code=201)
def delete_cart(users_id: int, db: Session = Depends(get_db), user: Users = Depends(get_current_admin)):
    delete_cart = db.query(Carts).filter(Carts.user_id == users_id).first()
    if not delete_cart:
        raise HTTPException(status_code=404, detail="cart bulunamadi")
    db.delete(delete_cart)
    db.commit()
    return {"message": "cart silindi"}


@app.put("/user/{users_id}/updateprofile", status_code=201)
def update_user_profile(user_update: UserUpdate, db: Session = Depends(get_db),):
    user = db.query(Users).filter(Users.id == user_update.id).first()
    
    user.username = user_update.username
    user.email = user_update.email
    user.hashed_password = user_update.password
    
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
   

    db.commit()
    db.refresh(user)    
       
    return UserResponse(username=user.username, email=user.email, hashed_password=user.hashed_password)
    

@app.post("/products/")
def create_product(product: ProductCreate, db: Session = Depends(get_db), user: Users = Depends(get_current_admin)):
    if not product.name:
        raise HTTPException(status_code=400, detail="urun adi olmadan")
    
    existing_product = db.query(Product).filter(Product.name == product.name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="urun adu")
    
    new_product = Product(name=product.name, stock=product.stock, price=product.price, category_id=product.category_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product





@app.get("/products/sorts/")
def get_products(db: Session = Depends(get_db),sort_by: str = Query(None, regex=("name|price|stock|$")), 
                order: str = Query("asc"), min_price: int = Query(None), max_price: int = Query(None)):
    query = db.query(Product)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
   
    if sort_by is not None:
        if order == "asc":
            query = query.order_by(sort_by)
        else:
            query = query.order_by(sort_by.desc()) 
    
    
    products = query.all()
    return products     



@app.post("/user/{user_id}/cart/{cart_id}/add_product", status_code=201)
def add_product_to_cart(user_id: int, cart_id: int, product_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    cart = db.query(Carts).filter(Carts.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Sepet bulunamadi")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadi")

    cart_item = CartItem(cart_id=cart_id, product_id=product_id,user_id=user_id)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Ürün sepete başariyla eklendi",
        "cart_item": {"cart_id": cart_item.cart_id, "product_id": cart_item.product_id, "user_id": cart_item.user_id},
    }


@app.get("/user/{user_id}/cart/{cart_id}/products")
def list_cart_products(user_id: int, cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(Carts).filter(Carts.id == cart_id, Carts.user_id == user_id).first()
    if not cart:
        print(f"Cart not found: cart_id={cart_id}, user_id={user_id}")
        raise HTTPException(status_code=404, detail="Sepet bulunamadi")

    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

    products = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        products.append({
            "product_id": product.id,
            "name": product.name,
            "stock": product.stock,
        })

    return {
        "cart_id": cart_id,
        "user_id": user_id,
        "products": products,
    }

#@app.get("/products/")
#async def read_item(skip: int = 0, limit: int=10):
#   return Product [skip: skip+limit]

@app.post("/category/create/")
def create_category(category: CategoryCreate, db: Session = Depends(get_db), user: Users = Depends(get_current_admin) ):
    new_category = Category(name=category.name, category_id=category.category_id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# @app.post("/products/create/")
# def create_product(product: ProductCreate, db: Session = Depends(get_db)):
#     new_product = Product(name=product.name, price=product.price, category_id=product.category_id)
#     db.add(new_product)
#     db.commit()
#     db.refresh(new_product)
#     return new_product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user: Users = Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    db.delete(product)
    db.commit()
    return {"message": "urun silindi"}


@app.post("/uploadfile/product/{product_id}")
async def create_upload_file(product_id: int,file: UploadFile = File(...), user: Users = Depends(get_current_admin)):
    FILEPATH = "./resim"
    filename = file.filename
    extension = filename.split(".")[1]
    
    if extension not in ["jpg", "png", "jpeg"]:
        return {"message": "onaylanmayan format"}
    
    token_name = secrets.token_urlsafe(16) + "." + extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    
    with open(generated_name, "wb") as file_object:
        file_object.write(file_content)
    
    img = Image.open(generated_name)
    img = img.resize((250, 250))    
    img.save(generated_name)
    
    return {
        "message": "Dosya başariyla yüklendi",
        "filename": generated_name,
        "uploaded_by": user.username,
    }






@app.post("/order/{user_id}/create", status_code=201)
def create_order(user_id: int, cart_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    cart = db.query(Carts).filter(Carts.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Sepet bulunamadi")
    
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Sepet boş")

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Ürün ID {item.product_id} bulunamadi")
        if product.stock <= 0:
            raise HTTPException(status_code=400, detail=f"Ürün '{product.name}' stokta yok")

        product.stock -= 1

    new_order = Order(user_id=user_id, cart_id=cart_id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

   


    
    return {
        "order_id": new_order.id,
        "message": "Sipariş başariyla oluşturuldu",
        "cart_items": [{"product_id": item.product_id, "quantity": 1} for item in cart_items],
    }

@app.get("/order/{user_id}", status_code=201)
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="siparis bulunamadi")
    return orders
    



@app.delete("/order/delete/{order_id}", status_code=201)
async def delete_order(order_id: int,  db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="siparis bulunamadi")
    db.delete(order)
    db.commit()     
    return {"detail": "siparis silindi"}






# @app.get("/products/{product_id}/comment")
# def get_product_comments(comment:CommentsBase,user_id=Comment.id, product_id=Comment.product_id,  db: Session = Depends(get_db),
#                          comments: str = Query(None),
#                          ):
#     comments_user = db.query(Comment).filter(Comment.comment == comment).first(),
#     comment=Comment(user_id=comments_user.id, product_id=comments_user.product_id, comment=comments_user.comment)
#     db_comment = Comment(userid=comment.id, product_id=comment.product_id, comment=comment.comment)
#     db.add(db_comment)
#     db.commit()
#     db.refresh(db_comment)
#     return comment

@app.post("/products/{product_id}/comment")
def get_product_comments(user_id: int, product_id: int,  comments: str, db: Session = Depends(get_db)):
    comments_user = db.query(Users).filter(Users.id==user_id).first()
    
    if comments_user is None:
        raise HTTPException(status_code=404, detail="kullanici yok")
    
    comments_product = db.query(Product).filter(Product.id==product_id).first()
    
    if comments_product is None:
        raise HTTPException(status_code=404, detail="urun yok")
    
    new_comment = Comment(
        user_id=user_id,
        product_id=product_id,
        comment=comments
    )
    
    db.add(new_comment)
    db.commit()
    return new_comment


@app.get("/products/{product_id}/comment")
def get_product_comments(product_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.product_id == product_id).all()
    if not comments:
        raise HTTPException(status_code=404, detail="yorum yok")
    return comments
    


@app.delete("/products/{product_id}/comment")
def delete_product_comments(product_id: int, db: Session = Depends(get_db), user: Users = Depends(get_current_admin)):
    comment = db.query(Comment).filter(Comment.product_id == product_id).first()
    db.delete(comment)
    db.commit()
    return {"detail": "yorum admin tarafindan silindi"} 
   
@app.get("/products/{product_id}/stock")
def get_product_stock(product_id: int, db: Session = Depends(get_db), user: Users = Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="urun yok")
    return product.stock




##############################################
manager = ConnectionManager()


@app.websocket("/ws/notifications")
async def notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            manager.add_message_to_queue(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/orders/{order_id}/update-status")
async def update_order_status(order_id: int, status: str, background_tasks: BackgroundTasks):
    message = {
        "order_id": order_id,
        "status": status,
    }
    websocket_messages = manager.get_messages_from_queue()
    for ws_message in websocket_messages:
        print(f"Received WebSocket message: {ws_message}")

    background_tasks.add_task(manager.broadcast, json.dumps(message))
    return {"message": "status güncellendi"}