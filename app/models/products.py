from sqlalchemy import Column, Integer, Numeric, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    rating = Column(Numeric(10, 2), default=0)  # new

    ratings = relationship(
        'Rating', back_populates='product', cascade='all, delete-orphan'
    )
    feedback = relationship(
        'Feedback', back_populates='product', cascade='all, delete-orphan'
    )
