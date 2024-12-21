from typing import Annotated, List
from fastapi import Depends, FastAPI, Path, status, HTTPException
from sqlalchemy import select, update, delete, insert, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.router import users
from app.router import ratings
from app.router import products
from app.router import feedback
from app.auth import get_current_user, auth
from app.backend.db import AsyncSession
from app.backend.db_depends import get_db
from app.models import Feedback, Product, Rating, User
from app.schemas import ProductReview, CreateRating, CreateFeedback


app = FastAPI()


app.include_router(users.router)
app.include_router(ratings.router)
app.include_router(products.router)
app.include_router(feedback.router)
app.include_router(auth.router)


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


@app.post('/add_review/{product_id}')
async def add_review(
    product_id: int,
    grade: int,
    comment: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)]
):
    async with db.begin():
        user_id = get_user.get('id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not authenticated'
            )

        product_query = await db.scalar(select(Product).filter(Product.id == product_id))
        if not product_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found'
            )

        existing_rating = await db.scalar(
            select(Rating).filter(
                Rating.user_id == user_id,
                Rating.product_id == product_id
            )
        )
        if existing_rating:
            existing_rating.grade = grade
        else:
            new_rating = Rating(
                grade=grade,
                user_id=user_id,
                product_id=product_id
            )
            db.add(new_rating)
            await db.flush()
        new_feedback = Feedback(
            comment=comment,
            user_id=user_id,
            product_id=product_id,
            rating_id=existing_rating.id if existing_rating else new_rating.id
        )
        db.add(new_feedback)

    return {
        'status_code': status.HTTP_200_OK,
        "detail": "Review added successfully"
    }


@app.post('/delete_review/{product_id}')
async def delete_review():
    pass
