from sqlalchemy import select, update, insert, delete
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.backend.db_depends import get_db
from app.schemas import CreateFeedback
from app.models.feedback import Feedback
from app.backend.db import AsyncSession


router = APIRouter(prefix='/feedback', tags=['feedback'])


@router.get('/')
async def get_all_feedback(db: Annotated[AsyncSession, Depends(get_db)]):
    feedback = await db.scalars(select(Feedback))
    result = feedback.all()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No feedback found'
        )

    return {
        'feedback': result
    }


@router.post('/')
async def create_feedback(create_feedback: CreateFeedback, db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(insert(Feedback).values(
        comment=create_feedback.comment,
        is_active=create_feedback.is_active,
        user_id=create_feedback.user_id,
        product_id=create_feedback.product_id,
        rating_id=create_feedback.rating_id
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Feedback created successfully'
    }


@router.put('/{feedback_id}')
async def update_feedback(db: Annotated[AsyncSession, Depends(get_db)], feedback_id: int, update_feedback: CreateFeedback):
    feedback = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Feedback not found'
        )

    await db.execute(update(Feedback).where(Feedback.id == feedback_id).values(
        comment=update_feedback.comment,
        is_active=update_feedback.is_active,
        user_id=update_feedback.user_id,
        product_id=update_feedback.product_id
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Feedback updated successfully'
    }


@ router.delete('/{feedback_id}')
async def delete_feedback(feedback_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    pass
