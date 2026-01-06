from __future__ import annotations
from pydantic import BaseModel
from typing import Generic,TypeVar,Optional

class Base_User(BaseModel):
    username: str
    email: str

class User_Create(Base_User):
    password: str

class User_Update(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class User_Out(Base_User):
    id: int

    class Config:
        from_attributes = True

T = TypeVar("T")
class Pagination(BaseModel,Generic[T]):
    total: int 
    page: int
    limit: int 
    objects: list[T]