from datetime import datetime
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from sqlalchemy import func, extract, or_
import math
from dateutil.relativedelta import relativedelta


from database.Budget import Budget
from database.Expense import Expense

class BudgetFacade:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.LOGGER = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def get_average_expense_for_all_budget(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[tuple[Budget, float]]:
        averages = []
        budgets: list[Budget] = self.db.query(Budget).options(joinedload(Budget.category_family)).all()
        for budget in budgets:
            average = self.get_average_expense_for_budget(
                budget_id=budget.id,
                start_date=start_date,
                end_date=end_date
            )
            averages.append((budget, average))
        return averages
    
    def get_average_expense_for_budget(
        self,
        budget_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """
        Calculate the average monthly or yearly expense amount for the budget's category family
        between start_date and end_date, based on the budget's frequency_type.
        """
        self.LOGGER.info(f"Calculating average for budget ID {budget_id} between {start_date} and {end_date}")
        budget: Budget = self.db.query(Budget).options(joinedload(Budget.category_family)).filter(Budget.id == budget_id).first()
        if not budget:
            return 0.0

        category_family_id = budget.category_family_id
        frequency_type = budget.frequency_type  # 0 = monthly, 1 = yearly
        self.LOGGER.info(f"Budget found for category_family_id {category_family_id} with frequency_type {frequency_type}")

        query = self.db.query(Expense).filter(
            Expense.category_family_id == category_family_id,
            or_(Expense.amount >= 0, Expense.calculation_status == "INCLUDE"),
            func.coalesce(Expense.calculation_status, '') != 'SKIP'
        )
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        print(query.order_by(Expense.date).all())
        avg = 0.0
        if start_date is None:
            start_date = self.db.query(func.min(Expense.date)).scalar()
        if end_date is None:
            end_date = datetime.now()
        if start_date is None or end_date is None:
            return avg
        delta = relativedelta(end_date, start_date)

        if frequency_type == 0:  # Monthly
            subquery = (
                query.with_entities(
                    extract('year', Expense.date).label('year'),
                    extract('month', Expense.date).label('month'),
                    func.sum(Expense.amount).label('monthly_sum')
                )
                .group_by('year', 'month')
                .subquery()
            )
            total_months = delta.years * 12 + delta.months
            if delta.days is not None or delta.days > 0:
                total_months += 1
            sum = self.db.query(func.sum(subquery.c.monthly_sum)).scalar()
            print(f"Total months: {total_months}, Sum: {sum}")
            if sum is None:
                sum = 0
            avg = sum / total_months
        elif frequency_type == 1:  # Yearly
            subquery = (
                query.with_entities(
                    extract('year', Expense.date).label('year'),
                    func.sum(Expense.amount).label('yearly_sum')
                )
                .group_by('year')
                .subquery()
            )
            total_years = math.ceil(delta.years + delta.months / 12) 
            sum = self.db.query(func.sum(subquery.c.yearly_sum)).scalar()
            if sum is None:
                sum = 0
            avg = sum / total_years if total_years > 0 else sum

        return avg