from unittest import result
from .. import models, schema, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import engine, get_db
from typing import List, Optional

router = APIRouter(
    prefix="/posts",# everything will be appended with this
    tags=["Posts"]
)

@router.get("/", response_model=List[schema.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute(""" SELECT * FROM posts  """)
    # posts = cursor.fetchall()
    
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    # inner join
    # select posts.*, count(votes.post_id) as total_votes from posts left join votes on posts.id = votes.post_id group by posts.id;
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("total_votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts

################create post################
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.PostResponse)
def create_posts(post: schema.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # post_dict = post.dict()
    # post_dict['id'] = randrange(0, 1000000)
    # my_posts.append(post_dict)
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *  """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()# commit the change in DB
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # the above one is inefficient, if you got 50 column, that you need to type 50 times.
    
    new_post = models.Post(owner_id = current_user.id, **post.dict()) # this one is better, automatically match the column
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)#like commit, these are sqlalchemy model

    return new_post 

# @router.get("/posts/latest") # demo that the url posts/latest cound technically match post/{id} and cause error
# def get_latest_post():
#     post = my_posts[len(my_posts)-1]
#     return {"latest post": post}

@router.get("/{id}", response_model=schema.PostOut) #{is} is the path parameter // it passes str
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # add :int to make sure it's int
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))# 'int' object does not support indexing, so convert it to str
    # post = cursor.fetchone()
    # print(test_post)
    # post = find_post(id) # to manipulate the server response
    # post = db.query(models.Post).filter(models.Post.id == id).first()#.first() to actually send the query and fetch the first match result
    
    post = db.query(models.Post, func.count(models.Vote.post_id).label("total_votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    print(post)
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, # cleaner way
                            detail = f"post with id: {id} was not found")
    if post.Post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} was not found"}
    return post

################delete posts################
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()# to make commit change to DB 
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post of this id doesn't exist")
    # check the user id to see if it's authorized to do it(if it's the post owner)
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)#actually doing the delete
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schema.PostResponse) 
def update_post(id: int, updated_post: schema.PostUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # makes sure the post comes with the right schema. (using the same class as create post)

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id), ))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post of this id doesn't exist")
    # check the user id to see if it's authorized to do it(if it's the post owner)
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    # post_query.update({'title': 'hey this is my updated title', 'content': 'this is my updated content'}, synchronize_session=False)
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post