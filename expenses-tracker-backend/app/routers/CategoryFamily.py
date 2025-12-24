import logging
from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from DatabaseSetup import SESSION_MAKER
from database.Budget import Budget
from database.Category import Category
from database.CategoryFamily import CategoryFamily
from sqlalchemy.orm import joinedload

from database.Expense import Expense
from database.Facades.CategoryFamilyFacade import CategoryFamilyFacade
from dto.CategoryDTO import CategoryDto
from dto.CategoryFamilyDto import CategoryFamilyDto
from dto.CombineCategoryFamilyDto import CombineCategoryFamilyDto

router = APIRouter(
    prefix="/category-family",
    tags=["category-family"],
    responses={404: {"description": "Not found"}},
)

LOGGER = logging.getLogger(__name__)

def serialize_category_family(categoryFamily: CategoryFamily) -> CategoryFamilyDto:
    return CategoryFamilyDto(
        id=categoryFamily.id,
        name=categoryFamily.name,
        regex_pattern=categoryFamily.regex_pattern,
        categories=None if categoryFamily.categories is None else [serialize_category(c) for c in categoryFamily.categories]
    )

def serialize_category(category: Category) -> CategoryDto:
    return CategoryDto(
        id=category.id,
        name=category.name,
        category_family_id=category.category_family_id
    )


@router.get("/", summary="Get all category families")
async def get_all_category_families():
    with SESSION_MAKER() as session:
        session: Session
        families = session.query(CategoryFamily).all()
        return [serialize_category_family(f) for f in families]
    

@router.patch("/{category_family_id}/regex", summary="Update regex_pattern for a CategoryFamily")
async def update_regex_pattern(category_family_id: int, regex_pattern: str | None = Body(..., embed=True)):
    if regex_pattern is not None and not regex_pattern.strip():
        regex_pattern = None
    with SESSION_MAKER() as session:
        session: Session
        family = session.query(CategoryFamily).filter_by(id=category_family_id).first()
        if not family:
            raise HTTPException(status_code=404, detail="CategoryFamily not found")
        family.regex_pattern = regex_pattern # type: ignore
        session.commit()
        session.refresh(family)
        return serialize_category_family(family)
    

@router.get("/mapping", summary="Get all category families with their mappings")
async def get_all_full_category_families():
    with SESSION_MAKER() as session:
        session: Session
        families = session.query(CategoryFamily).options(joinedload(CategoryFamily.categories)).all()
        return [serialize_category_family(f) for f in families]

@router.get("/{category_family_id}", summary="Get a category family by ID")
async def get_category_family(category_family_id: int):
    with SESSION_MAKER() as session:
        session: Session
        family = session.query(CategoryFamily).filter_by(id=category_family_id).first()
        if not family:
            raise HTTPException(status_code=404, detail="CategoryFamily not found")
        return serialize_category_family(family)
    

@router.patch("/combine", summary="Combine 2 category family into one. This will delete the second category family and move all categories to the first one")
async def add_category(combine_category_family: CombineCategoryFamilyDto):
    with SESSION_MAKER() as session:
        session: Session

        to_delete_family: CategoryFamily = session.query(CategoryFamily).filter_by(id=combine_category_family.deleting_cateogy_family_id).options(joinedload(CategoryFamily.categories)).first()
        surviving_category_family_db: CategoryFamily = session.query(CategoryFamily).filter_by(id=combine_category_family.surviving_cateogy_family_id).options(joinedload(CategoryFamily.categories)).first()

        if not to_delete_family:
            raise HTTPException(status_code=404, detail=f"To delete CategoryFamily with id {combine_category_family.deleting_cateogy_family_id} not found")
        
        if not surviving_category_family_db:
            raise HTTPException(status_code=404, detail=f"Surviving categoryFamily with id {combine_category_family.surviving_cateogy_family_id} not found")

        session.query(Expense)\
            .filter(Expense.category_family_id == to_delete_family.id)\
            .update({"category_family_id": surviving_category_family_db.id})
        
        session.query(Budget)\
            .filter(Budget.category_family_id == to_delete_family.id)\
            .update({"category_family_id": surviving_category_family_db.id})

        surviving_category_family_db.categories.extend(to_delete_family.categories)
        surviving_category_family_db.name = combine_category_family.name # type: ignore
        session.add(surviving_category_family_db)
        session.delete(to_delete_family)
        session.commit()

        return serialize_category_family(surviving_category_family_db)
    

@router.post("/recalculate-expense-category-family", summary="Recalculate category_family_id for all expenses based on regex_pattern")
async def recalculate_expense_category_family():
    with SESSION_MAKER() as session:
        session: Session
        families = session.query(CategoryFamily).filter(
            CategoryFamily.regex_pattern.isnot(None),
            CategoryFamily.regex_pattern != ''
        ).all()
        LOGGER.info(f"Found {len(families)} category families with regex patterns for recalculation.")
        batch_size = 1000
        updated_count = 0
        expenses_query = session.query(Expense).filter(Expense.lock_category == 0).yield_per(batch_size)


        for expense in expenses_query:
            LOGGER.debug(f"Processing expense id {expense.id} with description '{expense.description}' and original category '{expense.original_category}'")
            matched_family = None
            for family in families:
                LOGGER.debug(f"Checking against family id {family.id} with pattern '{family.regex_pattern}'")
                if expense.description and family.regex_pattern:
                    LOGGER.debug(f"Checking regex pattern '{family.regex_pattern}' against description '{expense.description}'")
                    import re
                    if re.search(family.regex_pattern, expense.description):
                        matched_family = family
                        LOGGER.info(f"Matched regex pattern '{family.regex_pattern}' for description '{expense.description}' for family '{family.name}'")
                        break
            if matched_family:
                if expense.category_family_id != matched_family.id:
                    expense.category_family_id = matched_family.id # type: ignore
                    updated_count += 1
                    LOGGER.info(f"Updated expense id {expense.id} to category family '{matched_family.name}'")
            else:
                catetogyFacade = CategoryFamilyFacade(session)
                category_family = catetogyFacade.get_or_create_by_category_name(expense.description, expense.original_category)
                if category_family and expense.category_family_id != category_family.id:
                    expense.category_family_id = category_family.id # type: ignore
                    updated_count += 1
                    LOGGER.info(f"No regex match. Set expense id {expense.id} to category family '{category_family.name}' based on original category")

        session.commit()
        LOGGER.info(f"Recalculation complete. Updated {updated_count} expenses.")
        return {"updated_expenses": updated_count}