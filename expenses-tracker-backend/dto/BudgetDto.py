from dataclasses import dataclass
from decimal import Decimal

from dto.CategoryFamilyDto import CategoryFamilyDto

@dataclass
class BudgetDto:
    id: int | None
    frequency_type: int
    target_amount: Decimal
    category_family: CategoryFamilyDto