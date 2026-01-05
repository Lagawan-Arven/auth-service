from fastapi import Depends,HTTPException,APIRouter
from sqlalchemy.orm import Session
import logging

from src.settings.dependencies import get_admin_access,get_session,get_pagination
from src.settings import models
from src import schemas

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/users",response_model=schemas.Pagination[schemas.User_Out])
def get_all_users(admin_access = Depends(get_admin_access),
                  session: Session = Depends(get_session),
                  pagination = Depends(get_pagination)):
    
    try:
        db_users = session.query(models.User)
        total = db_users.count()
        if not total:
            raise HTTPException(status_code=404,detail="There is no users yet")
        
        users = db_users.limit(pagination["limit"]).offset(pagination["offset"]).all()
        
        return {"total":total,"page":pagination['page'],"limit":pagination['limit'],"objects":users}
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.info("Internal Server Error | Getting all users failed")
        raise HTTPException(status_code=500,detail="Internal Server Error") from e