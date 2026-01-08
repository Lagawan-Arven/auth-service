from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import logging

from src.routers.login import router as login_router
from src.routers.users import router as users_router
from src.routers.admin import router as admin_router
from src.configurations.lifespan import lifespan
from src.configurations.logger import setup_logging
from src.configurations.rate_limit import limiter

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429,content={"message":"Too many requests"})

@app.get("/")
@limiter.limit("5/minute")
def app_started(request: Request,):
    logger.info("App started!")
    return {"message":"App started"}

app.include_router(login_router,tags=["Authentication"])
app.include_router(users_router,tags=["User"])
app.include_router(admin_router,tags=["Admin-only"])
