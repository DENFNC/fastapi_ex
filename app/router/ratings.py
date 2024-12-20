from sqlalchemy import select, update, insert, delete
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.backend.db_depends import get_db
from app.schemas import CreateRating
from app.models.rating import Rating
from app.backend.db import AsyncSession


router = APIRouter(prefix='/rating', tags=['rating'])


@router.get('/')
async def get_all_product_rating(db: Annotated[AsyncSession, Depends(get_db)]):
    rating = await db.scalars(select(Rating))
    result = rating.all()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No ratings found'
        )
    return {
        'ratings': result
    }


@router.get('/detail/{product_id}')
async def get_product_rating_detail(db: Annotated[AsyncSession, Depends(get_db)], product_id):
    rating = await db.scalar(select(Rating).where(Rating.product_id == product_id, Rating.is_active == True))
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Rating not found for the given product'
        )
    return {
        'rating': rating
    }


@ router.post('/')
async def create_product_rating(db: Annotated[AsyncSession, Depends(get_db)], create_rating: CreateRating):
    await db.execute(insert(Rating).values(
        grade=create_rating.grade,
        user_id=create_rating.user_id,
        product_id=create_rating.product_id,
        is_active=create_rating.is_active
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Rating created successfully'
    }


@ router.put('/{rating_id}')
async def update_product_rating(db: Annotated[AsyncSession, Depends(get_db)], rating_id: int, update_rating: CreateRating):
    await db.execute(update(Rating).where(Rating.id == rating_id).values(
        grade=update_rating.grade,
        user_id=update_rating.user_id,
        product_id=update_rating.product_id,
        is_active=update_rating.is_active
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Rating updated successfully'
    }


@ router.delete('/{rating_id}')
async def delete_product_rating(db: Annotated[AsyncSession, Depends(get_db)], rating_id: int):
    await db.execute(update(Rating).where(Rating.id == rating_id).values(
        is_active=False
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Rating deleted successfully'
    }
