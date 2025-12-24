from dataclasses import dataclass

from dto.BudgetDto import BudgetDto

@dataclass
class CreateExpensePayload:
  description: str
  amount: float
  date: str
  category_name: str
  sourceId: int