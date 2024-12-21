from sqlalchemy import func, select, update, insert, delete
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.backend.db_depends import get_db
from app.schemas import CreateRating
from app.models import Rating, Product
from app.backend.db import AsyncSession


router = APIRouter(prefix='/rating', tags=['rating'])


async def calculate_average_rating(db: AsyncSession, product_id: int) -> float:
    result = await db.execute(
        select(func.avg(Rating.grade))
        .where(Rating.product_id == product_id, Rating.is_active == True)
    )
    average = result.scalar()
    return average if average is not None else 0.0


@router.get('/')
async def get_all_product_rating(db: Annotated[AsyncSession, Depends(get_db)]):
    rating = await db.scalars(select(Rating).where(Rating.is_active == True))
    result = rating.all()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No active ratings found'
        )
    return {
        'ratings': result
    }


@router.get('/detail/{product_id}')
async def get_product_rating_detail(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    rating = await db.scalar(select(Rating).where(Rating.product_id == product_id, Rating.is_active == True))
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Rating not found for the given product'
        )
    return {
        'rating': rating
    }


@router.post('/')
async def create_product_rating(db: Annotated[AsyncSession, Depends(get_db)], create_rating: CreateRating):
    async with db.begin():
        await db.execute(insert(Rating).values(
            grade=create_rating.grade,
            user_id=create_rating.user_id,
            product_id=create_rating.product_id,
            is_active=create_rating.is_active
        ))

        average_rating = await calculate_average_rating(db, create_rating.product_id)

        await db.execute(
            update(Product)
            .where(Product.id == create_rating.product_id)
            .values(rating=average_rating)
        )

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Rating created successfully'
    }


@router.put('/{rating_id}')
async def update_product_rating(db: Annotated[AsyncSession, Depends(get_db)], rating_id: int, update_rating: CreateRating):
    async with db.begin():
        await db.execute(update(Rating).where(Rating.id == rating_id).values(
            grade=update_rating.grade,
            user_id=update_rating.user_id,
            product_id=update_rating.product_id,
            is_active=update_rating.is_active
        ))

        average_rating = await calculate_average_rating(db, update_rating.product_id)

        await db.execute(
            update(Product)
            .where(Product.id == update_rating.product_id)
            .values(average_rating=average_rating)
        )

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Rating updated successfully'
    }


@router.delete('/{rating_id}')
async def delete_product_rating(db: Annotated[AsyncSession, Depends(get_db)], rating_id: int):
    async with db.begin():
        result = await db.execute(
            select(Rating).where(Rating.id == rating_id)
        )
        rating = result.scalar_one_or_none()
        if rating is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Rating not found'
            )

        rating.is_active = False
        db.add(rating)

        await calculate_average_rating(db, rating.product_id)

    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Rating deleted successfully'
    }
