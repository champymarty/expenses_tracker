from sqlalchemy import Column, Integer, Text
from database.Base import Base

from sqlalchemy.orm import relationship


class CategoryFamily(Base):
    __tablename__ = 'category_family'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    regex_pattern = Column(Text, nullable=True)

    categories = relationship("Category", back_populates="category_family")
    expenses = relationship("Expense", back_populates="category_family")
    budgets = relationship("Budget", back_populates="category_family")

