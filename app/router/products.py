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
    product = await db.scalars(select(Product).where(Product.is_active == True))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    return {
        'Products': product
    }


@router.post('/')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct):
    await db.execute(insert(Product).values(
        name=create_product.name,
        description=create_product.description,
        price=create_product.price
    ))
    await db.commit()
    return {
        'Product': 'Created successfully'
    }
