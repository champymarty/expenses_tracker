from sqlalchemy import Column, Integer, Text
from database.Base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, unique=True, nullable=False)

    expenses = relationship("Expense", back_populates="user")
