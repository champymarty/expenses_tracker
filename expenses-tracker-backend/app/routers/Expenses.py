from datetime import datetime
import logging
from typing import List, Optional

from fastapi.params import Query
from sqlalchemy.orm import Session
from DatabaseSetup import SESSION_MAKER
from database.Expense import Expense
from database.Facades.ExpenseFacade import ExpenseFacade
from fastapi import APIRouter, File, HTTPException, UploadFile

from database.Source import Source
from dto.ExpenseDto import ExpenseDto
from dto.ExpensesUpload import ExpensesUpload
from extractors.FileExtractor import FileExtractor
from extractors.FileExtractorCreator import FileExtractorCreator

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    responses={404: {"description": "Not found"}},
)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

@router.get("/", summary="Get expenses between start and end date")
async def get_expenses_between_dates(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"), # type: ignore
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format") # type: ignore
):
    start_date_datetime = None
    if start_date:
        start_date_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_datetime = None
    if end_date:
        end_date_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    expenses = []
    with SESSION_MAKER() as session:
        session: Session
        expenseFacade = ExpenseFacade(session)
        expenses = expenseFacade.get_expenses_between_dates(
            start_date=start_date_datetime,
            end_date=end_date_datetime
        )


    serialized_expenses = [serialize_expense(e) for e in expenses]

    return {"expenses": serialized_expenses}

@router.patch("/{expense_id}", summary="Update an expense from UI")
async def update_expense(
    expense_id: int,
    expense_update: ExpenseDto,
):
    with SESSION_MAKER() as session:
        session: Session
        expense = session.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        new_category_id = expense_update.categoryFamily.id if expense_update.categoryFamily else None        
        if new_category_id is None:
            raise HTTPException(status_code=400, detail="Category ID cannot be null")
        if new_category_id != expense.category_family_id:
            expense.category_family_id = new_category_id # type: ignore
            LOGGER.info(f"Updated category familly id to {expense.category_family_id} for expense {expense.id}. Also locking category as manual update.")
            expense_update.lock_category = True # if source changes, lock_category must be true
        else:
            LOGGER.info(f"Category Familly ID {expense.source_id} remains unchanged for expense {expense.id}")

        lock_category = expense_update.lock_category
        if lock_category is None:
            lock_category = False
        if lock_category != expense.lock_category:
            expense.lock_category = lock_category # type: ignore
            LOGGER.info(f"Updated lock_category to {expense.lock_category} for expense {expense.id}")

        calculation_status = expense_update.calculation_status
        if calculation_status != expense.calculation_status:
            expense.calculation_status = calculation_status # type: ignore
            LOGGER.info(f"Updated calculation_status to {expense.calculation_status} for expense {expense.id}")
        else:
            LOGGER.info(f"calculation_status {expense.calculation_status} remains unchanged for expense {expense.id}")
            

        session.commit()
        session.refresh(expense)

        return serialize_expense(expense)

# Serialize expenses
def serialize_expense(expense: Expense) -> ExpenseDto:
    return ExpenseDto(
        id=expense.id,
        date=expense.date,
        description=expense.description,
        amount=float(expense.amount),
        original_category=expense.original_category,
        lock_category=expense.lock_category,
        source=expense.source,
        calculation_status=expense.calculation_status,
        user=expense.user if expense.user else None,
        categoryFamily=expense.category_family
    )


@router.post("/{source_id}/upload/", summary="Upload Excel file to load expenses")
async def upload_expenses(
    source_id: int,
    files: List[UploadFile] = File(...),
):
    source: Source | None = None
    with SESSION_MAKER() as session:
        session: Session
        source = session.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    expensesUpload = ExpensesUpload(0, 0)
    try:
        for file in files:
            LOGGER.info(f"Processing file: {file.filename} for source: {source.name}")
            extractor: FileExtractor = FileExtractorCreator.create_extractor(file, source)
            new_expensesUpload = await extractor.extract()
            expensesUpload.created_expenses += new_expensesUpload.created_expenses
            expensesUpload.existing_expenses += new_expensesUpload.existing_expenses
    except Exception as e:
        print(f"Error creating extractor: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    return expensesUpload