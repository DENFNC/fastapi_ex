from typing import Annotated, Optional
from passlib.hash import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import insert, select, update
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.models.users import User
from app.backend.db import AsyncSession
from app.backend.db_depends import get_db
from app.schemas import CreateUser


router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'])
oauth_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
SECRET_KEY = 'fdc051c88582294af77a16a63e696a211421a478042e2f6cee201a4b72c89f42'
ALGORITHM = 'HS256'


async def create_access_token(username: str, user_id: str, is_admin: bool, expires_delta: timedelta):
    to_encode = {
        'username': username,
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + expires_delta
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(username, user_id, is_admin, expires_delta):
    to_encode = {
        'username': username,
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + expires_delta
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.password) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )

    return user


async def get_current_user(token: Annotated[str, Depends(oauth_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('user_id')
        username: str = payload.get('username')
        is_admin: bool = payload.get('is_admin', False)
        expire = payload.get('exp')

        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        return {
            'username': username,
            'id': int(user_id),
            'is_admin': is_admin,
        }
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


@router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {'User': user}


@router.post('/token')
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(db, form_data.username, form_data.password)

    access_token = await create_access_token(
        username=user.username,
        user_id=user.id,
        is_admin=user.is_admin,
        expires_delta=timedelta(minutes=10)
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


@router.post('/refresh')
async def refresh_token_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    token_request: str
):
    refresh_token = token_request.refresh_token

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('username')
        user_id: str = payload.get('user_id')
        is_admin: bool = payload.get('is_admin')
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token has expired'
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token'
        )

    if not username or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload'
        )

    user = await db.scalar(select(User).where(User.id == user_id))
    if not user or user.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token'
        )

    access_token_expires = timedelta(minutes=15)
    new_access_token = await create_access_token(
        username=user.username,
        user_id=user.id,
        is_admin=user.is_admin,
        expires_delta=access_token_expires
    )

    return {
        'access_token': new_access_token,
        'token_type': 'bearer'
    }


@router.post('/')
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_user: CreateUser
):

    async with db.begin():
        result = await db.execute(
            insert(User).values(
                username=create_user.username,
                email=create_user.email,
                password=bcrypt.hash(create_user.password),
            ).returning(User.id, User.username, User.is_admin)
        )
        user = result.fetchone()
        if not user:
            raise Exception("User creation failed")

        refresh_token = await create_refresh_token(
            username=user.username,
            user_id=user.id,
            is_admin=user.is_admin,
            expires_delta=timedelta(days=7)
        )

        await db.execute(
            update(User).where(User.id == user.id).values(
                refresh_token=refresh_token)
        )

    return {
        'status_code': status.HTTP_201_CREATED,
        'message': 'User created successfully',
        'refresh_token': refresh_token
    }
