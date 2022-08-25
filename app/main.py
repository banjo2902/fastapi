
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tkinter import Tk, ttk
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings

# this is the command that told sqlalchemy to run the create statement so that it generates all the table when starting up
# since we have alembic, we don't need it anymore:
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # you can define what requests are allowed
    allow_headers=["*"], # you can define what headers are allowed
)

app.include_router(post.router)# refer to post router
app.include_router(user.router)# refer to user router
app.include_router(auth.router)# refer to user router
app.include_router(vote.router)# refer to user router

@app.get("/") # decorator
def root():
    return {"message": "welcome to my api!!!"}

# test sqlalchemy
# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#     posts = db.query(models.Post).all()#??
#     return {"data": posts}

