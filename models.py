from database import Base
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    role = Column(String, default="user")
    
    
    comments = relationship('Comment', back_populates='users')
    orders = relationship('Order', back_populates='users')
    cart_items = relationship('CartItem', back_populates='users')  # Eklenen ilişki

class Carts(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    cart_items = relationship('CartItem', back_populates='carts')
    orders = relationship('Order', back_populates='carts')

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  

    carts = relationship("Carts", back_populates="cart_items")
    products = relationship("Product", back_populates="cart_items")
    users = relationship("Users", back_populates="cart_items")  

    class Config:
        orm_mode = True

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))

    products = relationship('Product', back_populates='category')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String,  nullable=False)  
    stock = Column(Integer, nullable=False) 
    price = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    
    category = relationship('Category', back_populates='products')
    cart_items = relationship('CartItem', back_populates='products')
    comments = relationship("Comment", back_populates="products")
    
    
class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    comment = Column(String, nullable=False)
    
    users = relationship("Users", back_populates="comments")
    products = relationship("Product", back_populates="comments")
    
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    cart_id = Column(Integer, ForeignKey('carts.id'))
    
    carts = relationship('Carts', back_populates='orders')
    users = relationship('Users', back_populates='orders')
