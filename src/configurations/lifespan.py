from contextlib import asynccontextmanager
import logging,os

from src.configurations.database import engine

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):

    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")

    engine.dispose()