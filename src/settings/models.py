from sqlalchemy.orm import declarative_base
from sqlalchemy import String,Integer,Column,DateTime
from datetime import datetime,timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,unique=True,autoincrement=True)
    role = Column(String,default="user")
    username = Column(String)
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime,default=datetime.now(timezone.utc))
    updated_at = Column(DateTime,default=datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))