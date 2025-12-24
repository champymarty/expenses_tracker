from fastapi import APIRouter, status, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import joinedload, Session
from DatabaseSetup import SESSION_MAKER
from database.Category import Category
from dto.CategoryDTO import CategoryDto

router = APIRouter(
    prefix="/category",
    tags=["category"],
    responses={404: {"description": "Not found"}},
)

def serialize_category(category: Category) -> CategoryDto:
    return CategoryDto(
        id=category.id,
        name=category.name,
        category_family_id=category.category_family_id
    )

@router.post("/", summary="Add a new category to a category family")
async def add_category(category: CategoryDto):
    with SESSION_MAKER() as session:
        session: Session
        # Case-insensitive check for existing category name
        existing_category: Category = session.query(Category).options(joinedload(Category.category_family)).filter(
            func.lower(Category.name) == category.name.lower()
        ).first()
        if existing_category:
            raise HTTPException(status_code=409, detail=f"Category name {category.name} already exists in {existing_category.category_family.name} category family")
        
        new_category = Category(
            name=category.name,
            category_family_id=category.category_family_id
        )
        session.add(new_category)
        session.commit()
        session.refresh(new_category)

        return serialize_category(new_category)

@router.delete("/{category_id}", summary="Delete a category by ID", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int):
    with SESSION_MAKER() as session:
        session: Session
        category = session.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        session.delete(category)
        session.commit()