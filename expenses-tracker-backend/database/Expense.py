from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from database.Base import Base


class Expense(Base):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    original_category = Column(Text, nullable=True)
    lock_category = Column(Integer, nullable=False, default=0)  # 0 = False, 1 = True
    calculation_status = Column(Text, nullable=True, default=None) # SKIP, INCLUDE

    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    source_id = Column(Integer, ForeignKey('source.id'), nullable=False)
    category_family_id = Column(Integer, ForeignKey('category_family.id'), nullable=False)


    user = relationship("User", back_populates="expenses")
    source = relationship("Source", back_populates="expenses")
    category_family = relationship("CategoryFamily", back_populates="expenses")

    __table_args__ = (
        UniqueConstraint("description", "amount", "date", "user_id", "source_id", name="unique_expense_constraint"),
    )