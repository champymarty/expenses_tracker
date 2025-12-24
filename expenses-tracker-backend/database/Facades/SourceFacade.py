from datetime import datetime
from typing import Optional
from sqlalchemy import extract, func, or_
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta

from database.Expense import Expense
from database.Source import Source
from dto.SourceAverage import SourceAverage


class SourceFacade:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create_by_name(self, name: str) -> Source:
        """
        Get a Source by name, or create it if it doesn't exist.
        Returns the Source instance.
        """
        source = self.session.query(Source).filter_by(name=name).first()
        if not source:
            source = Source(name=name)
            self.session.add(source)
            self.session.commit()
            self.session.refresh(source)
        return source
    
    def get_average_expense_for_sources(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[SourceAverage]:

        query = self.session.query(Expense).filter(
            or_(Expense.amount >= 0, Expense.calculation_status == "INCLUDE"),
            or_(Expense.calculation_status != "SKIP", Expense.calculation_status.is_(None))
        )
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        avg = 0.0
        if start_date is None:
            start_date = self.session.query(func.min(Expense.date)).scalar()
        if end_date is None:
            end_date = datetime.now()
        if start_date is None or end_date is None:
            return []
        delta = relativedelta(end_date, start_date)

        subquery = (
            query.with_entities(
                extract('year', Expense.date).label('year'),
                extract('month', Expense.date).label('month'),
                Expense.source_id.label('source_id'),
                func.sum(Expense.amount).label('monthly_sum')
            )
            .group_by("source_id", "year", "month")
            .subquery()
        )
        total_months = delta.years * 12 + delta.months
        if delta.days is not None or delta.days > 0:
            total_months += 1
        result = self.session.query(
            Source,
            (func.sum(subquery.c.monthly_sum) / total_months).label("average_expense")
        ).join(Source, Source.id == subquery.c.source_id) \
         .group_by(Source.id).all()

        return [SourceAverage(source=source, average=average_expense) for source, average_expense in result]