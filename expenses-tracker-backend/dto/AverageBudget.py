from dataclasses import dataclass

from dto.BudgetDto import BudgetDto

@dataclass
class AverageBudgetDto:
    budget: BudgetDto
    average: float