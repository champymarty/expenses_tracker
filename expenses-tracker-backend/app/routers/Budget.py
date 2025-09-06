from datetime import datetime
from typing import Optional

from fastapi.params import Query
from sqlalchemy.orm import Session
from DatabaseSetup import SESSION_MAKER
from database.CategoryFamily import CategoryFamily
from database.Budget import Budget
from database.Facades.BudgetFacade import BudgetFacade
from fastapi import APIRouter, HTTPException

from dto.AverageBudget import AverageBudgetDto
from dto.BudgetDto import BudgetDto

router = APIRouter(
    prefix="/budget",
    tags=["budgets"],
    responses={404: {"description": "Not found"}},
)

@router.delete("/{budget_id}", summary="Delete a budget by ID")
async def delete_budget(budget_id: int):
    with SESSION_MAKER() as session:
        session: Session
        budget = session.query(Budget).filter(Budget.id == budget_id).first()
        if budget is None:
            raise HTTPException(status_code=404, detail="Budget not found")
        session.delete(budget)
        session.commit()
        return {"detail": f"Budget with id {budget_id} deleted successfully."}

@router.post("/", summary="Create a new budget")
async def create_budget(budget: BudgetDto):
    with SESSION_MAKER() as session:
        session: Session
        # Check if the category_family exists
        found_budget = session.query(Budget).filter(
            Budget.category_family_id == budget.category_family.id,
            Budget.frequency_type == budget.frequency_type
        ).first()
        if found_budget is not None:
            raise HTTPException(status_code=409, detail="Budget already exist")
        new_budget = Budget(
            frequency_type=budget.frequency_type,
            target_amount=budget.target_amount,
            category_family_id=budget.category_family.id
        )
        session.add(new_budget)
        session.commit()
        session.refresh(new_budget)
        return {
            "id": new_budget.id,
            "frequency_type": new_budget.frequency_type,
            "target_amount": new_budget.target_amount,
            "category_family_id": new_budget.category_family_id
        }



@router.get("/calculate", summary="Calculate the all the budgets for the given interval. Budget can have either monthly or yearly average.")
async def get_budget_averages_between_dates(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"), # type: ignore
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format") # type: ignore
):
    print(f"Received request to calculate budget averages between {start_date} and {end_date}")
    start_date_datetime = None
    if start_date:
        start_date_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_datetime = None
    if end_date:
        end_date_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    print(f"Start date: {start_date_datetime}, End date: {end_date_datetime}")

    averages = []
    with SESSION_MAKER() as session:
        session: Session
        expenseFacade = BudgetFacade(session)
        averages = expenseFacade.get_average_expense_for_all_budget(
            start_date=start_date_datetime,
            end_date=end_date_datetime
        )


    serialized_averages = [serialize_average_budget(e) for e in averages]

    return {"averages": serialized_averages}

def serialize_average_budget(average_budget: tuple[Budget, float]) -> AverageBudgetDto:
    return AverageBudgetDto(
        budget=BudgetDto(
            id=average_budget[0].id,
            frequency_type=average_budget[0].frequency_type,
            target_amount=average_budget[0].target_amount,
            category_family=average_budget[0].category_family
        ),
        average=average_budget[1]
    )