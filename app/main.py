from typing import Annotated, List
from fastapi import Depends, FastAPI, Path, status, HTTPException
from sqlalchemy import select, update, delete, insert, func
from sqlalchemy.orm import selectinload
import uvicorn

from app.router import users
from app.router import ratings
from app.router import products
from app.router import feedback
from app.backend.db import AsyncSession
from app.backend.db_depends import get_db
from app.models import Feedback, Product, Rating, User
from app.schemas import ProductReview


app = FastAPI()


app.include_router(users.router)
app.include_router(ratings.router)
app.include_router(products.router)
app.include_router(feedback.router)


@app.get('/')
async def get_resource():
    return {'message': 'Hello, FastAPI!'}


@app.get('/all_reviews', response_model=List[ProductReview])
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        result = await db.execute(
            select(Product)
            .options(selectinload(Product.feedback))
        )
        products = result.scalars().all()

        if not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No products found'
            )

        return [
            ProductReview(
                name=product.name,
                description=product.description,
                price=product.price,
                rating=product.rating,
                feedback=[feedback.comment for feedback in product.feedback]
            )
            for product in products
        ]
    except Exception as e:
        print(e)


@app.get('/product_review/{product_id}', response_model=List[ProductReview])
async def get_product_review(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    try:
        result = await db.execute(
            select(Product)
            .options(selectinload(Product.feedback))
            .where(Product.id == product_id)
        )
        products = result.scalars().all()

        if not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No products found'
            )

        return [
            ProductReview(
                name=product.name,
                description=product.description,
                price=product.price,
                rating=product.rating,
                feedback=[feedback.comment for feedback in product.feedback]
            )
            for product in products
        ]
    except Exception as e:
        print(e)
