from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date

from app.backend.db import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, nullable=False)
    comment = Column(Text, default='No comment')
    comment_date = Column(Date, default=date.today)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    rating_id = Column(Integer, ForeignKey('ratings.id'), nullable=True)

    user = relationship('User', back_populates='feedback')
    product = relationship('Product', back_populates='feedback')
    rating = relationship('Rating', back_populates='feedback')
