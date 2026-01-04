from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timezone,timedelta

from src.configurations.environment import ENV
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_ACCESS_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes="bcrypt")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password,hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_ACCESS_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,ALGORITHM)