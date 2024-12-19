from sqlalchemy import select, update, insert, delete
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.backend.db_depends import get_db
from app.schemas import CreateFeedback
from app.models.feedback import Feedback
from app.backend.db import AsyncSession


router = APIRouter(prefix='/feedback', tags=['feedback'])


@router.get('/')
async def get_all_feedback():
    pass


@router.post('/')
async def create_feedback(feedback: CreateFeedback, db: Annotated[AsyncSession, Depends(get_db)]):
    pass


@router.put('/{feedback_id}')
async def update_feedback(feedback_id: int, feedback: CreateFeedback, db: Annotated[AsyncSession, Depends(get_db)]):
    pass


@router.delete('/{feedback_id}')
async def delete_feedback(feedback_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    pass
