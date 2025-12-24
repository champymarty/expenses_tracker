from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.Base import Base


class Source(Base):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    card_number = Column(String(4), nullable=False)

    expenses = relationship("Expense", back_populates="source")
