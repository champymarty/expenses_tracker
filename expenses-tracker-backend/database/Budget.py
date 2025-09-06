from sqlalchemy import Column, Float, ForeignKey, Integer
from database.Base import Base
from sqlalchemy.orm import relationship


class Budget(Base):
    __tablename__ = 'budget'
    id = Column(Integer, primary_key=True, autoincrement=True)
    frequency_type = Column(Integer, unique=False, nullable=False)
    target_amount = Column(Float, unique=False, nullable=False)

    category_family_id = Column(Integer, ForeignKey('category_family.id'), nullable=False)
    category_family = relationship("CategoryFamily", back_populates="budgets")

