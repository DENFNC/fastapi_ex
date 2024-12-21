from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy import select, update, insert
from passlib.hash import bcrypt

from app.models.users import User
from app.backend.db_depends import get_db
from app.backend.db import AsyncSession
from app.schemas import CreateUser


router = APIRouter(prefix='/user', tags=['user'])


@router.post('/')
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    async with db.begin():
        await db.execute(insert(User).values(
            username=create_user.username,
            email=create_user.email,
            password=bcrypt.hash(create_user.password)
        ))

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'User created successfully'
    }


@router.put('/{user_id}')
async def update_user(db: Annotated[AsyncSession, Depends(get_db)], user_id: int, user_update: CreateUser):
    async with db.begin():
        user = await db.scalar(select(User).where(User.id == user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        await db.execute(update(User).where(User.id == user_id).values(
            username=user_update.username,
            email=user_update.email,
            password=bcrypt.hash(user_update.password)
        ))

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User updated successfully'
    }


@router.delete('/{user_id}')
async def delete_user(db: Annotated[AsyncSession, Depends(get_db)], user_id: int):
    async with db.begin():
        user = await db.scalar(select(User).where(User.id == user_id))

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        await db.execute(update(User).where(User.id == user_id).values(is_active=False))

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User deleted successfully'
    }
