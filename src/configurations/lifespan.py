from contextlib import asynccontextmanager
import logging,os

from src.configurations.database import engine,session
from src.settings import models
from src.settings.auth import hash_password

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):

#======================================================
#           CREATE AN ADMIN ACCOUNT
#======================================================
    my_session = session()
    try:
        db_admin = my_session.query(models.User).filter(models.User.role=="admin").first()
        if not db_admin:
            new_admin = models.User(
                role = "admin",
                username = "admin",
                email = "admin@email.com",
                password = hash_password(password="1234")
            )
            my_session.add(new_admin)
            my_session.commit()
    finally:
        my_session.close()

    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")

    engine.dispose()