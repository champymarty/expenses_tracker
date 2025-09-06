import logging
from sqlalchemy.orm import Session

from database.Category import Category
from database.CategoryFamily import CategoryFamily


class CategoryFamilyFacade:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def get_or_create_by_category_name(self, expense_description: str | None, category_name: str) -> CategoryFamily:
        """
        Get or create a CategoryFamily and Category by category_name.
        - If a CategoryFamily with the given name exists, returns it.
        - Otherwise, creates a new CategoryFamily and a Category linked to it.
        Returns the CategoryFamily instance.
        """

        self.logger.info(f"Getting or creating CategoryFamily for category name and description: {category_name}, {expense_description}")

        if expense_description is not None:
            # Try to find a CategoryFamily by matching the regex_pattern with the expense_description
            family = self.session.query(CategoryFamily).filter(
                CategoryFamily.regex_pattern.isnot(None),
                CategoryFamily.regex_pattern != ''
            ).all()
            for f in family:
                import re
                if re.search(f.regex_pattern, expense_description, re.IGNORECASE):
                    self.logger.info(f"Matched regex pattern '{f.regex_pattern}' for description '{expense_description}' for family '{f.name}'")
                    return f

        # Get or create the Category
        category = self.session.query(Category).filter_by(name=category_name).first()
        if category:
            self.logger.info(f"Category found: {category.name}")
            return category.category_family
            

        family = CategoryFamily(name=category_name)
        self.session.add(family)
        self.session.commit()
        self.session.refresh(family)
        self.logger.info(f"Created new CategoryFamily: {family.name}")

        category = Category(
            category_family_id=family.id,
            name=category_name
        )
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        self.logger.info(f"Created new Category: {category.name} under Family: {family.name}")
        
        return family