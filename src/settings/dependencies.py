from fastapi import Depends,HTTPException,Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt

from src.configurations.database import session
from src.settings.auth import SECRET_KEY,ALGORITHM
from src.settings import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login_form")

def get_session():
    my_session = session()
    try:
        yield my_session
    finally:
        my_session.close()

def get_current_user(token = Depends(oauth2_scheme),session: Session = Depends(get_session)) -> models.User:
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id = int(payload.get("id"))
    except:
        raise HTTPException(status_code=406,detail="Invalid token")
    
    db_user = session.get(models.User,user_id)
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found")
    
    return db_user

def get_admin_access(current_user = Depends(get_current_user)) -> models.User:

    if current_user.role != "admin":
        raise HTTPException(status_code=401,detail="Unauthorized")
    return current_user

def get_pagination(page:int = Query(1,ge=1),limit:int = Query(10,ge=1,le=1000)):

    offset = (page - 1)*limit
    return {"page":page,"limit":limit,"offset":offset}