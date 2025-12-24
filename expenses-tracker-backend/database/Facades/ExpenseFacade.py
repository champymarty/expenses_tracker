from datetime import datetime
import logging
from typing import Optional
from sqlalchemy import DateTime
from sqlalchemy.orm import Session, Query
from sqlalchemy.orm import joinedload

from database.Facades.SourceFacade import SourceFacade
from database.Expense import Expense
from database.Facades.CategoryFamilyFacade import CategoryFamilyFacade

class ExpenseFacade:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.extracted = set()
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def get_expense_by_details(self, description: str, amount: float, date: datetime, source_id: int | None) -> Optional[Expense]:
        return self.db.query(Expense).filter_by(description=description, amount=amount, date=date, source_id=source_id).first()
    
    def is_multiple_row_in_same_extract(self, description: str, amount: float, date: datetime, source_id: int | None) -> bool:
        count = self.db.query(Expense).filter_by(description=description, amount=amount, date=date, source_id=source_id).count()
        return count > 1

    def create_expense(self, description: str, amount: float, date: datetime, category_name: str, source_id: int) -> Expense | None:
        catetogyFacade = CategoryFamilyFacade(self.db)
        category_family = catetogyFacade.get_or_create_by_category_name(description, category_name)

        self.logger.info(f"Creating expense: {description}, {amount}, {date}, {category_family.name}, {source_id}")
        if (description, amount, date, source_id) in self.extracted:
            self.logger.warning(f"Duplicate expense in the same extract: {description}, {amount}, {date}, {source_id}. Will not consider as duplicate in DB.")
        else:
            existing_expense = self.get_expense_by_details(description, amount, date, source_id)
            if existing_expense:
                self.logger.info(f"Expense already exists: {existing_expense.description}, {existing_expense.amount}, {existing_expense.date}. Not saving duplicate.")
                return None
        

        new_expense = Expense(description=description,
                               amount=amount,
                                date=date,
                                original_category=category_name,
                                source_id=source_id,
                                category_family_id=category_family.id
        )
        self.db.add(new_expense)
        self.extracted.add((description, amount, date, source_id))
        return new_expense
    
    def get_expenses_between_dates(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> list[Expense]:
        query: Query = self.db.query(Expense).options(joinedload(Expense.source), joinedload(Expense.category_family), joinedload(Expense.user))
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        return query.all()