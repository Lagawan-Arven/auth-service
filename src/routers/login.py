from sqlalchemy.orm import Session
from fastapi import HTTPException,Depends,APIRouter
from fastapi.security import OAuth2PasswordRequestForm
import logging,hashlib
from datetime import datetime,timezone,timedelta

from src import schemas
from src.settings.dependencies import get_session,get_current_user
from src.settings.auth import hash_password,verify_password,create_access_token,create_refresh_token
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
            logger.info("User account already existed | User registration failed")
            raise HTTPException(status_code=400,detail="User account already existed | User registration failed")
        
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
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | User registration failed")
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
            logger.info("User account not found | User login failed")
            raise HTTPException(status_code=404,detail="User account not found | User login failed")
        
        if not verify_password(password,hashed_password=db_user.password):
            logger.info("Password did not match | User login failed")
            raise HTTPException(status_code=404,detail="Password did not match | User login failed")
        
        if db_user.status == "restricted":
            logger.info("Your account have been restricted | User login failed")
            raise HTTPException(status_code=403,detail="Your account have been restricted | User login failed")

        access_token = create_access_token({"id":db_user.id,"role":db_user.role})
        raw_refresh_token, hashed_refresh_token = create_refresh_token()

        logger.info("User login successfull | username: %s",db_user.username)
        return {"message":"User login successfull","access_token":access_token,"token_type":"bearer","refresh_token":raw_refresh_token}
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | User login failed")
        raise HTTPException(status_code=500,detail="Internal Server Error") from e
    
#======================================================
#                   LOGIN OAUTH2
#======================================================
@router.post("/login_form")
def login_user(form:OAuth2PasswordRequestForm = Depends(),
               session: Session = Depends(get_session)) -> dict:
    
    try:
        db_user = session.query(models.User).filter(models.User.username==form.username).first()
        if not db_user:
            logger.info("User account not found | User login failed")
            raise HTTPException(status_code=404,detail="User account not found | User login failed")
        
        if not verify_password(form.password,hashed_password=db_user.password):
            logger.info("Password did not match | User login failed")
            raise HTTPException(status_code=404,detail="Password did not match | User login failed")

        if db_user.status == "restricted":
            logger.info("Your account have been restricted | User login failed")
            raise HTTPException(status_code=403,detail="Your account have been restricted | User login failed")

        access_token = create_access_token({"id":db_user.id,"role":db_user.role})
        raw_refresh_token, hashed_refresh_token = create_refresh_token()

        new_refresh_token = models.Refresh_Token(
            refresh_token = hashed_refresh_token,
            expire_at = datetime.now(timezone.utc) + timedelta(days=7),
            user = db_user
        )
        session.add(new_refresh_token)
        session.commit()

        logger.info("User login successfull | username: %s",db_user.username)
        return {"message":"User login successfull","access_token":access_token,"token_type":"bearer","refresh_token":raw_refresh_token}
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | User login failed")
        raise HTTPException(status_code=500,detail="Internal Server Error") from e
    
#======================================================
#                   REFRESH ENPOINT
#======================================================
@router.get("/refresh")
def refresh(refresh_token: str,
            current_user = Depends(get_current_user),
            session: Session = Depends(get_session)):
    
    hash_token = hashlib.sha256(refresh_token.encode()).hexdigest()
    db_refresh_token = session.query(models.Refresh_Token).filter(
        models.Refresh_Token.refresh_token == hash_token,
        models.Refresh_Token.is_revoked == False,
        models.Refresh_Token.expire_at > datetime.now(timezone.utc)
    ).first()
    if not db_refresh_token:
        logger.info("Invalid refresh token")
        raise HTTPException(status_code=400,detail="Invalid refresh token")
    
    access_token = create_access_token({"id":current_user.id,"role":current_user.role})
    logger.info("Refresh successfull")
    return {"message":"Refresh successful","access_token":access_token,"refresh_token":refresh_token}

#======================================================
#                   LOGOUT USER
#======================================================
@router.post("/logout")
def logout_user(refresh_token: str,
            current_user = Depends(get_current_user),
            session: Session = Depends(get_session) ):
    
    hash_token = hashlib.sha256(refresh_token.encode()).hexdigest() 
    db_refresh_token = session.query(models.Refresh_Token).filter(models.Refresh_Token.refresh_token==hash_token).first()
    if db_refresh_token:
        db_refresh_token.is_revoked = True
        session.commit()
    logger.info("User logout")
    return {"message":"User logout"}
