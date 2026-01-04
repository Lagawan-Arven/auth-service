from sqlalchemy.orm import Session
from fastapi import HTTPException,Depends,APIRouter
import logging

from src import schemas
from src.settings.dependencies import get_session
from src.settings.auth import hash_password,verify_password,create_access_token
from src.settings import models

logger = logging.getLogger(__name__)

router = APIRouter()

#======================================================
#                   REGISTER USER
#======================================================
@router.post("/register",response_model=schemas.User_Out)
def register_user(user_data: schemas.User_Create,
                  session: Session = Depends(get_session)):

    try:
        #Checks if the user already registered
        db_user = session.query(models.User).filter(models.User.username==user_data.username).first()
        if db_user:
            logger.info("User account already exist")
            raise HTTPException(status_code=400,detail="User account already exist")
        
        hashed_password = hash_password(user_data.password)
        new_user = models.User(
            username = user_data.username,
            email = user_data.email,
            password = hashed_password
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info("User account created successfully | username: %s",user_data.username)
        return new_user
    except HTTPException:
        session.rollback()
        logger.info("User registration failed")
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error")
        raise HTTPException(status_code=500,detail="Internal Server Error") from e

#======================================================
#                   LOGIN USER
#======================================================
@router.post("/login")
def login_user(username: str,password: str,
               session: Session = Depends(get_session)) -> dict:
    
    try:
        db_user = session.query(models.User).filter(models.User.username==username).first()
        if not db_user:
            logger.info("User account not found")
            raise HTTPException(status_code=404,detail="User account not found")
        
        if not verify_password(password,hashed_password=db_user.password):
            logger.info("Password did not match")
            raise HTTPException(status_code=404,detail="Password did not match")
        
        access_token = create_access_token({"id":db_user.id,"role":db_user.role})

        logger.info("User login successfull | username: %s",db_user.username)
        return {"message":"User login successfull","access_token":access_token,"token_type":"bearer"}
    except HTTPException:
        session.rollback()
        logger.info("User login failed")
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error")
        raise HTTPException(status_code=500,detail="Internal Server Error") from e