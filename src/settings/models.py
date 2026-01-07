from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import String,Integer,Column,DateTime,ForeignKey,Boolean
from datetime import datetime,timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,unique=True,autoincrement=True)
    role = Column(String,default="user")
    status = Column(String, default="active")
    username = Column(String)
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime,default=datetime.now(timezone.utc))
    updated_at = Column(DateTime,default=datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))

    refresh_token = relationship("Refresh_Token",back_populates="user",cascade="all, delete-orphan")

class Refresh_Token(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer,primary_key=True,unique=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"))
    refresh_token = Column(String)
    is_revoked = Column(Boolean,default=False)
    created_at = Column(DateTime,default=datetime.now(timezone.utc))
    expire_at = Column(DateTime)

    user = relationship("User",back_populates="refresh_token")