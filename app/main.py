from typing  import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import FastAPI
from fastapi.params import Body
from typing import Optional
from random import randrange
import psycopg2

from psycopg2.extras import RealDictCursor
import time
from . import database, utils
from . import models, oath2
from . import schemas
from sqlalchemy.orm import Session 
from sqlalchemy import func
# import sys
from .database import engine, SessionLocal, get_db
from fastapi.middleware.cors import CORSMiddleware

from .schemas import PostOut

# don't need it, used for create table models
# models.Base.metadata.create_all(bind=engine)


## all path operation
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def root():
    return {"message":"hello!!ttest"}


# stored memory
# my_posts = [{"title":"title of post 1", "contect":"content of post 1","id": 1}, 
#             {"title":"title of post 2", "contect":"content of post 2","id": 2}

#             ]


# def find_post(id):
#     for p in my_posts:
#         if p['id'] == id:
#             return p
        

# def find_index_post(id):
#     for i,p in enumerate(my_posts):
#         if p['id'] == id:
#             return i

# request get method url: "/"

# @app.get("/post")
# async def root():
#     return {"message": "Hello World dddd!!!"}

# @app.get("/sqlalchemy")
# def test_posts(db:Session = Depends(get_db)):
#     posts = db.query(models.Post).all()
#     return {"data":posts}




@app.get("/posts", response_model= List[PostOut])
def get_posts(db:Session =Depends(get_db), get_current_user : int = Depends(oath2.get_current_user), limit : int = 10, skip: int =0, search: Optional[str] = ""):
    # cursor.execute("""select * from posts""")
    # posts = cursor.fetchall()
    # print(posts)
    posts = db.query(models.Post) \
            .filter(models.Post.title.contains(search)) \
            .limit(limit).offset(skip).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
    .outerjoin(models.Vote, models.Vote.post_id == models.Post.id) \
    .group_by(models.Post.id).filter(models.Post.title.contains(search)) \
            .limit(limit).offset(skip).all()
    post_out_list = [
        schemas.PostOut(
            id=post.id,
            title=post.title,
            content=post.content,
            owner_id=post.owner_id,
            created_at=post.created_at,
            votes=votes if votes else 0
        )
        for post, votes in results
    ]
    # posts = db.query(models.Post).all()
    # posts = db.query(models.Post).filter(models.Post.owner_id == get_current_user.id ).all()
    return post_out_list

# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)):
#     print (payload)
#     return {"message":"create"}



# @app.post("/createposts")
# def create_posts(new_post:Post):
#     print (new_post)
#     print(new_post.dict())
#     return {"data":new_post}



# create a post
@app.post("/posts", status_code= status.HTTP_201_CREATED, response_model= schemas.Post)
def create_posts(post:schemas.PostCreat, db:Session =Depends(get_db), get_current_user : int = Depends(oath2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id = get_current_user.id, **post.dict())
    # new_post = models.Post(title = post.title, content = post.content, published = post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    # return {"data":new_post}
    return new_post

# @app.get("/posts/{id}")
# def get_post(id):
#     post = find_post(id)
#     return{"post_detail": f"here is post{id}"}



# @app.get("/posts/latest")
# def get_latest():
#     post = my_posts[len(my_posts)-1]
#     return {"detail": post}

#get an individual post
@app.get("/posts/{id}", response_model= schemas.Post)
def get_post(id: int, db:Session =Depends(get_db), get_current_user : int = Depends(oath2.get_current_user) ): 
    # cursor.execute(""" select * from posts where id = %s """, (str(id),))
    # post = cursor.fetchone()
   
    post = db.query(models.Post).filter(models.Post.id == id).first()
    # print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"post with id {id} was not found")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Not authorized to perform requested action")
    # return{"post_detail": post}
    # format shape of response
    return post

## delete using sql
# @app.delete("/posts/{id}",  status_code= status.HTTP_204_NO_CONTENT)
# def delet_post(id: int):
#     # deleting post
#     # find the index in the arry that has required ic
#     # my_posts.pop(index)
#     # index= find_index_post(id)
#     cursor.execute("""delete from posts where id = %s returning *""",(str(id),))
#     deleted_post = cursor.fetchone()
#     conn.commit()


@app.delete("/posts/{id}",  status_code= status.HTTP_204_NO_CONTENT)
def delet_post(id: int,  db:Session =Depends(get_db), get_current_user : int = Depends(oath2.get_current_user)  ):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"post with id {id} was not found")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    # return {'message':'post was successfuly deleted'}
    

# update post using put using sql

# @app.put("/posts/{id}")
# def update_posts(id:int, post: Post):

#     cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""",
#                    (post.title,post.content, post.published, str(id)))
#     updated_post = cursor.fetchone()
#     conn.commit()
    
#     if updated_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail= f"post with id {id} was not found")

#     return {'data':updated_post}


@app.put("/posts/{id}", response_model= schemas.Post)
def update_posts(id:int, updated_post: schemas.PostCreat,  db:Session =Depends(get_db), get_current_user : int = Depends(oath2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"post with id {id} was not found")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Not authorized to perform requested action")
    

    post_query.update(updated_post.dict(), synchronize_session= False)
    db.commit()

    return post_query.first()





@app.get('/users/{id}', response_model = schemas.UserOut)
def get_user(id:int, db: Session = Depends(get_db), get_current_user : int = Depends(oath2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"user with id:{id} does not exist")
    return user
     

# create a user
@app.post("/users", status_code= status.HTTP_201_CREATED, response_model = schemas.UserOut)
def create_posts(user:schemas.UserCreate, db:Session =Depends(get_db)):
    # hash the pw - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    # new_post = models.Post(title = post.title, content = post.content, published = post.published)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@app.post("/login", status_code= status.HTTP_201_CREATED, response_model= schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    # username =, password = 
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    #print(user)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail= f"invalid credential")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail= f"invalid credential")
    
    access_token = oath2.create_access_token(data = {"user_id": user.id})
    # create a token
    # return token
    return {"access_token":access_token, "token_type":"bearer"}


@app.post("/vote", status_code= status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db:Session = Depends(database.get_db), current_user:int = Depends(oath2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"post with id: {vote.post_id} does not exist")
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if (vote.dir == 1):
       if found_vote:
           raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail = f"user {current_user.id} has already voted on post {vote.post_id}")
       new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
       db.add(new_vote)
       db.commit()
       return {"message":"successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Vote does not exist")
        vote_query.delete(synchronize_session = False
                          )
        db.commit()

        return {"message":"successfully deleted vote"}