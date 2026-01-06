from typing import Optional
from fastapi import Depends,HTTPException,APIRouter
from sqlalchemy import or_
from sqlalchemy.orm import Session
import logging

from src.settings.dependencies import get_admin_access,get_session,get_pagination
from src.settings import models
from src import schemas

router = APIRouter()

logger = logging.getLogger(__name__)

#======================================================
#                  GET ALL USERS
#======================================================
@router.get("/users")
def get_all_users(admin_access = Depends(get_admin_access),
                  session: Session = Depends(get_session),
                  pagination = Depends(get_pagination)):
    
    try:
        db_users = session.query(models.User)
        total = db_users.count()
        if not total:
            raise HTTPException(status_code=404,detail="There is no users yet | Getting all users failed")
        
        users = db_users.limit(pagination["limit"]).offset(pagination["offset"]).all()
        
        return {"total":total,"page":pagination['page'],"limit":pagination['limit'],"objects":users}
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | Getting all users failed")
        raise HTTPException(status_code=500,detail="Internal Server Error | Getting all users failed") from e

#======================================================
#           GET USER BY ID OR EMAIL OR USERNAME
#======================================================
@router.get("/users/user")
def get_user(id:Optional[int] = None, email:Optional[str] = None, username:Optional[str] = None,
            admin_access = Depends(get_admin_access),
            session: Session = Depends(get_session)):
    try:
        db_user = session.query(models.User).filter(
            or_(
            models.User.id==id,
            models.User.email==email,
            models.User.username==username
            )  
        ).first()
        if not db_user:
            raise HTTPException(status_code=404,detail="User not found | Getting user failed")
        
        return db_user
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | Getting user failed")
        raise HTTPException(status_code=500,detail="Internal Server Error | Getting user failed") from e
    
#======================================================
#           RESTRICTING A USER ACCOUNT
#======================================================
@router.post("/users")
def restrict_user(id:Optional[int] = None, email:Optional[str] = None, username:Optional[str] = None,
                admin_access = Depends(get_admin_access),
                session: Session = Depends(get_session)):
    try:
        db_user = session.query(models.User).filter(
            or_(
            models.User.id==id,
            models.User.email==email,
            models.User.username==username
            )  
        ).first()
        if not db_user:
            logger.info("User not found | Restricting user failed")
            raise HTTPException(status_code=404,detail="User not found | Restricting user failed")
        if db_user.role =="admin":
            logger.info("User admin cannot be restricted | Restricting user failed")
            raise HTTPException(status_code=403,detail="User admin cannot be restricted!")
        
        db_user.status = "restricted"
        session.commit()
        session.refresh(db_user)
        return db_user
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | Restricting user failed")
        raise HTTPException(status_code=500,detail="Internal Server Error | Restricting user failed") from e
    
#======================================================
#           UNRESTRICTING A USER ACCOUNT
#======================================================
@router.put("/users")
def unrestrict_user(id:Optional[int] = None, email:Optional[str] = None, username:Optional[str] = None,
                admin_access = Depends(get_admin_access),
                session: Session = Depends(get_session)):
    try:
        db_user = session.query(models.User).filter(
            or_(
            models.User.id==id,
            models.User.email==email,
            models.User.username==username
            )  
        ).first()
        if not db_user:
            logger.info("User not found | Unrestricting user failed")
            raise HTTPException(status_code=404,detail="User not found | Unrestricting user failed")
        if db_user.role =="admin":
            logger.info("User admin cannot be restricted/unrestricted")
            raise HTTPException(status_code=403,detail="User admin cannot be restricted/unrestricted!")
        if db_user.status == "active" or "deactivated":
            logger.info("User is not restricted")
            raise HTTPException(status_code=400,detail="User is not restricted")
        
        db_user.status = "active"
        session.commit()
        session.refresh(db_user)
        return db_user
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | Restricting user failed")
        raise HTTPException(status_code=500,detail="Internal Server Error | Restricting user failed") from e