from fastapi import FastAPI
import logging

from src.routers.login import router as login_router
from src.routers.users import router as users_router
from src.routers.admin import router as admin_router
from src.configurations.lifespan import lifespan
from src.configurations.logger import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

@app.get("/")
def app_started():
    logger.info("App started!")
    return {"message":"App started"}

app.include_router(login_router,tags=["Authentication"])
app.include_router(users_router,tags=["User"])
app.include_router(admin_router,tags=["Admin-only"])
