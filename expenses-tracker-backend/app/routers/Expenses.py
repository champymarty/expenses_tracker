from datetime import datetime
import logging
from typing import List, Optional
import os
from pathlib import Path

from fastapi.params import Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from DatabaseSetup import SESSION_MAKER, export_database
from database.Expense import Expense
from database.Facades.ExpenseFacade import ExpenseFacade
from fastapi import APIRouter, File, HTTPException, UploadFile

from database.Source import Source
from dto.ExpenseDto import ExpenseDto
from dto.ExpensesUpload import ExpensesUpload
from dto.FileFailedToExtract import FileFailedToExtract
from extractors.FileExtractor import FileExtractor
from extractors.FileExtractorCreator import FileExtractorCreator
from payloads.CreateExpensePayload import CreateExpensePayload

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    responses={404: {"description": "Not found"}},
)

LOGGER = logging.getLogger(__name__)

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


@router.post("/upload/", summary="Upload Excel file to load expenses")
async def upload_expenses(
    source_id: Optional[int] = None,
    files: List[UploadFile] = File(...),
):
    source: Source | None = None

    if source_id is not None:
        with SESSION_MAKER() as session:
            session: Session
            source = session.query(Source).filter(Source.id == source_id).first()

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
    
    expensesUpload = ExpensesUpload(0, 0)
    try:
        for file in files:
            LOGGER.info(f"Processing file: {file.filename} for source: {source.name if source else 'AUTO-DETECT'}")
            if not file or not file.filename:
                LOGGER.warning(f"File is empty or not provided: {file.filename}")
                raise HTTPException(status_code=400, detail="No file provided or file is empty.")
            
            extractors: list[FileExtractor] = await FileExtractorCreator.create_extractor(file, source)
            if not extractors or len(extractors) == 0:
                LOGGER.warning(f"No extractor found for file: {file.filename}")
                expensesUpload.filesFailedToExtract.append(FileFailedToExtract(filename=file.filename, reason=f"No extractor found for the file {file.filename}."))
            elif len(extractors) > 1:
                LOGGER.warning(f"Multiple extractors found for file: {file.filename}. Cannot proceed.")
                classes = [extractor.__class__ for extractor in extractors]
                expensesUpload.filesFailedToExtract.append(FileFailedToExtract(filename=file.filename,
                                                                                reason=f"Multiple extractors: {classes} found for the file."))
            else:
                extractor = extractors[0]
                LOGGER.info(f"Using extractor {extractor.__class__.__name__} for file: {file.filename}")
                new_expensesUpload = await extractor.extract()
                expensesUpload.created_expenses += new_expensesUpload.created_expenses
                expensesUpload.existing_expenses += new_expensesUpload.existing_expenses
                expensesUpload.filesFailedToExtract.extend(new_expensesUpload.filesFailedToExtract)
                LOGGER.info(f"File {file.filename} processed. Created expenses: {new_expensesUpload.created_expenses}, Existing expenses: {new_expensesUpload.existing_expenses}")
    except Exception as e:
        LOGGER.error(f"Error creating extractor")
        raise HTTPException(status_code=400, detail=str(e))
    
    return expensesUpload

@router.post("/", summary="Create a new expense", status_code=201)
async def create_expense(expense: CreateExpensePayload):
    with SESSION_MAKER() as session:
        session: Session
        expense_facade = ExpenseFacade(session)
        
        new_expense = expense_facade.create_expense(
            description=expense.description,
            amount=float(expense.amount),
            date=datetime.strptime(expense.date, "%Y-%m-%d"),
            category_name=expense.category_name,
            source_id=expense.sourceId
        )
        
        if not new_expense:
            raise HTTPException(
                status_code=409,
                detail="An expense with the same details already exists"
            )
        
        session.commit()
        session.refresh(new_expense)
        
        return serialize_expense(new_expense)


@router.get("/export/database", summary="Export database as SQLite file")
async def export_database_endpoint():
    """
    Export the entire expenses database as a SQLite file.
    Returns the database file as a downloadable attachment.
    """
    db_path = Path("expenses_tracker.db")
    
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database file not found")
    
    try:
        LOGGER.info(f"Exporting database from {db_path}")
        file_path = export_database()

        return FileResponse(
            path=file_path,
            media_type="application/sql",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"},
        )
    except Exception as e:
        LOGGER.error(f"Error exporting database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting database: {str(e)}")