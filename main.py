from os import stat
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from starlette.status import HTTP_404_NOT_FOUND


app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

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
def get_posts():
    cursor.execute(""" SELECT * from posts """)
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING 
    * """, 
                    (post.title, post.content, post.published))

    new_post = cursor.fetchone()

    conn.commit()
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
    cursor.execute("""UPDATE posts SELECT title = %s, content = %s, published = %s RETURNING 
    * """, 
                    (post.title, post.content, post.published))
    updated_post = cursor.fetchone()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"post with id: {id} does not exist")
    return {"data": updated_post}