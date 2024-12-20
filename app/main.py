from typing import Annotated
from fastapi import Depends, FastAPI, status, HTTPException
from sqlalchemy import select, update, delete, insert, func

from app.router import users
from app.router import ratings
from app.router import products
from app.router import feedback
from app.backend.db import AsyncSession
from app.backend.db_depends import get_db
from app.models import Feedback, Product, Rating, User


app = FastAPI()


app.include_router(users.router)
app.include_router(ratings.router)
app.include_router(products.router)
app.include_router(feedback.router)


@app.get('/')
async def get_resource():
    return {'message': 'Hello, FastAPI!'}


@app.get('/all_reviews')
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(
            Product.name,
            Product.description,
            Product.price,
            Product.rating,
            func.array_agg(Feedback.comment).label('comments')
        )
        .join(Feedback, Feedback.product_id == Product.id)
        .group_by(Product.id)
    )
    reviews = result.mappings().all()

    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No reviews found'
        )

    return {
        'Reviews': reviews
    }
