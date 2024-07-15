from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

class UserCreate(BaseModel):
    email:EmailStr
    password:str


class UserOut(BaseModel):
    email:EmailStr
    id:int
    created_at: datetime
    class config:
        orm_mode = True


class UserLogin(BaseModel):
    email:EmailStr
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]





# define schema
# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True
#     # rating: Optional[int] = None


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


# expend basemodel
class PostCreat(PostBase):
    pass

# Post response
class Post(PostBase):
    id: int
    # title:str
    # content: str
    # published: bool
    owner_id: int
    created_at: datetime
    owner: UserOut
    class config:
        orm_mode = True


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime
    votes: int  # Make sure to include votes if it's part of your response

    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) # type: ignore

