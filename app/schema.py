from datetime import datetime
import email
from operator import le
from pydantic import BaseModel, EmailStr, conint
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr # special datatype from pydantic, make sure it's email format
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    #create_at: datetime = None
    class Config:
        orm_mode = True

class userAuth(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    #create_at: datetime
    owner_id: int
    owner: UserOut
    class Config:
        orm_mode = True
    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes).

class PostOut(BaseModel):
    Post: PostResponse
    total_votes: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)#less than equal 1


# class CreatePost(BaseModel):
#     title: str
#     content: str
#     publsihed: bool = True

# class UpdatePost(BaseModel):
#     title: str
#     content: str
#     publsihed: bool