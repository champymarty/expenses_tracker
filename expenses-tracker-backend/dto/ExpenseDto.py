
from datetime import datetime

from dataclasses import dataclass

from dto.CategoryFamilyDto import CategoryFamilyDto
from dto.SourceDto import SourceDto
from dto.UserDto import UserDto

@dataclass
class ExpenseDto:
  id: int
  date: datetime
  description: str
  amount: float
  original_category: str
  lock_category: int  # 0 = False, 1 = True
  calculation_status: str | None

  source: SourceDto
  user: UserDto | None
  categoryFamily: CategoryFamilyDto
