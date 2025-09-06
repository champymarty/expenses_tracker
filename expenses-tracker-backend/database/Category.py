from sqlalchemy import Column, ForeignKey, Integer, Text
from database.Base import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=False, nullable=False)

    category_family_id = Column(Integer, ForeignKey('category_family.id'), nullable=False)
    
    category_family = relationship("CategoryFamily", back_populates="categories")