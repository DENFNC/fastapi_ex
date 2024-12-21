from sqlalchemy import select, update, insert, delete
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.backend.db_depends import get_db
from app.schemas import CreateProduct
from app.models.products import Product
from app.backend.db import AsyncSession


router = APIRouter(prefix='/product', tags=['product'])


@router.get('/')
async def get_all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    product = await db.scalars(select(Product))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    return {
        'Products': product.all()
    }


@router.get('/detail/{product_id}')
async def get_detail_product(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    product = await db.scalar(select(Product).where(Product.id == product_id))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    return product


@router.post('/')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct):
    async with db.begin():
        await db.execute(insert(Product).values(
            name=create_product.name,
            description=create_product.description,
            price=create_product.price
        ))

    return {
        'status_code': status.HTTP_201_CREATED,
        'Product': 'Created successfully'
    }


@router.put('/{product_id}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_id: int, update_product: CreateProduct):
    async with db.begin():
        product = await db.scalar(select(Product).where(Product.id == product_id))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found'
            )
        await db.execute(update(Product).where(Product.id == product_id).values(
            name=update_product.name,
            description=update_product.description,
            price=update_product.price
        ))

    return {
        'status_code': status.HTTP_200_OK,
        'Product': 'Updated successfully'
    }
