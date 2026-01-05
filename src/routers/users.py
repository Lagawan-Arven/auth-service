from fastapi import Depends,HTTPException,APIRouter
import logging

from src.settings.dependencies import get_current_user
from src import schemas

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/user",response_model=schemas.User_Out)
def get_current_user_info(current_user = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=404,detail="User not found")

    return current_user