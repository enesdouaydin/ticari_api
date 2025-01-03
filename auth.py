from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import  JWTError, jwt
from sqlalchemy.orm import Session
from crud import get_user_by_username, verify_password
from passlib.context import CryptContext
from database import get_db
from models import Users 

SECRET_KEY = "avsv55s6v5a56+656ghgh54665421536244$%^%^&#$TRTDFGh35#%^#$%^"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




def hashed_password(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def authenticate_category(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt\
        
        
# def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     user_role = db.query(Users).filter(Users.role == user_role).first()
#     if user_role == "admin":
#         raise HTTPException(status_code=200, detail="Kullanici bilgisi bulundu")
#     else:
#         raise HTTPException(status_code=400, detail="Kullanici bilgisi bulunamadi") 
    
    
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_role = payload.get("role")
        if user_role != "admin":
            raise HTTPException(status_code=403, detail="Admin yetkisi gereklidir")
        
        user = db.query(Users).filter(Users.username == payload.get("sub")).first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
        
        return user
    except JWTError:
        raise HTTPException(status_code=403, detail="Geçersiz token")