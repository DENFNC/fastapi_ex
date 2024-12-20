from datetime import datetime
from pydantic import BaseModel
from typing import Union, List


class CreateUser(BaseModel):
    username: str
    email: str
    password: str


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float


class CreateRating(BaseModel):
    grade: int = 0
    user_id: int
    product_id: int
    is_active: bool = True


class CreateFeedback(BaseModel):
    comment: str
    is_active: bool = True
    user_id: int
    product_id: int
    rating_id: int


class ProductReview(BaseModel):
    name: str
    description: str
    price: float
    rating: float
    feedback: Union[List[str], str]
