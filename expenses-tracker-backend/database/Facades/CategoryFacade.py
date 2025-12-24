from typing import Optional
from sqlalchemy.orm import Session

from database.Category import Category



class CategoryFacade:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_category_by_name(self, name: str) -> Optional[Category]:
        category = self.db_session.query(Category).filter(Category.name == name).first()
        if category:
            return category
        return None