from fastapi import Depends,HTTPException,APIRouter
from sqlalchemy.orm import Session
import logging
from typing import Annotated

from src.settings import models
from src.settings.dependencies import get_current_user, get_session
from src.settings.auth import hash_password
from src import schemas

router = APIRouter()

logger = logging.getLogger(__name__)

#======================================================
#                GET CURRENT USER INFO
#======================================================
@router.get("/users/me",response_model=schemas.User_Out)
def get_current_user_info(current_user: Annotated[get_current_user,Depends]):
    if current_user.status == "deactivated":
        raise HTTPException(status_code=403,detail="Your account is deactivated")
    return current_user

#======================================================
#             UPDATE/EDIT CURRENT USER INFO
#======================================================
@router.put("/users/me",response_model=schemas.User_Out)
def update_user_account(update_data: schemas.User_Update,
                current_user:models.User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    try:
        db_user = session.get(models.User,current_user.id)
        if db_user.status == "deactivated":
            raise HTTPException(status_code=403,detail="Your account is deactivated | User account update failed")
        if update_data.username != "string":
            db_user.username = update_data.username
            session.flush()
        if update_data.email != "string":
            db_user.email = update_data.email
            session.flush()
        if update_data.password != "string":
            new_password = hash_password(update_data.password)
            db_user.password = new_password
            session.flush()

        session.commit()
        session.refresh(db_user)
        logger.info("User account updated successfully | username: %s",db_user.username)
        return db_user
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | User account update failed")
        raise HTTPException(status_code=500,detail="Internal Server Error | User account update failed") from e
    
#======================================================
#                   DEACTIVATE ACCOUNT
#======================================================
@router.post("/users/me")
def deactive_user_account(current_user = Depends(get_current_user),
                          session: Session = Depends(get_session)):
    if current_user.status == "deactivated":
        raise HTTPException(status_code=400,detail="Your account is already deactivated")
    current_user.status = "deactivated"
    session.commit()
    logger.info("User account deactivated successfully | username: %s",current_user.username)
    return {"message":"User account deactivated successfully"}

#======================================================
#                   REACTIVATE ACCOUNT
#======================================================
@router.patch("/user/me")
def reactivate_user_account(current_user = Depends(get_current_user),
                          session: Session = Depends(get_session)):
    if current_user.status == "active":
        raise HTTPException(status_code=400,detail="Your account is already active")
    current_user.status = "active"
    session.commit()
    logger.info("User account reactivated successfully | username: %s",current_user.username)
    return {"message":"User account reactivated successfully"}
#======================================================
#                   DELETE ACCOUNT
#======================================================
@router.delete("/users/me")
def delete_user_account(current_user = Depends(get_current_user),
                        session: Session = Depends(get_session)):
    
    db_user = session.get(models.User,current_user.id)
    session.delete(db_user)
    session.commit()
    logger.info("User account deleted successfully | username: %s",current_user.username)
    return {"message":"User account deleted successfully"}