from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.configurations.environment import ENV
import os 

DB_URL = os.getenv('DB_URL')
if not DB_URL:
    raise RuntimeError("Database is not set-up")

engine = create_engine(DB_URL)
session = sessionmaker(autoflush=False,bind=engine)
