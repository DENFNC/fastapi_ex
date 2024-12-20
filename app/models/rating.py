from sqlalchemy import Column, ForeignKey, Integer, Boolean, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'product_id',
            name='_user_product_rating_uc'
        ),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    grade = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    is_active = Column(Boolean, default=True)

    product = relationship('Product', back_populates='ratings')
    user = relationship('User', back_populates='ratings')
    feedback = relationship(
        'Feedback',
        back_populates='rating',
        cascade='all, delete-orphan',
        uselist=False
    )
