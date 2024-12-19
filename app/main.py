from fastapi import FastAPI

from app.router import users
from app.router import ratings
from app.router import products
from app.router import feedback

app = FastAPI()


@app.get('/')
async def get_resource():
    return {'message': 'Hello, FastAPI!'}

app.include_router(users.router)
app.include_router(ratings.router)
app.include_router(products.router)
app.include_router(feedback.router)
