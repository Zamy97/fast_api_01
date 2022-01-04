from os import stat
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body

from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy import engine
from starlette.status import HTTP_404_NOT_FOUND
import time
import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind = engine)


app = FastAPI()





while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'fastapi01', user = 'postgres', password = '@Fariha143', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("ERROR: ", error)
        time.sleep(5)

@app.get("/")
def root():
    return {"message": "Hello World!!!"}


@app.get("/posts")
def get_posts(db: Session =  Depends(get_db)):
    # cursor.execute(""" SELECT * from posts """)
    # posts = cursor.fetchall()

    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_a_posts(post: Post, db: Session =  Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING 
    # * """, 
    #                 (post.title, post.content, post.published))

    # new_post = cursor.fetchone()

    # conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
def get_one_post(id: int):
    cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    one_post = cursor.fetchone()
    if not one_post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return {"post_detail": one_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts where id = %s RETURNING *""",(str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING 
    * """, 
                    (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"post with id: {id} does not exist!")
    return {"data": updated_post}