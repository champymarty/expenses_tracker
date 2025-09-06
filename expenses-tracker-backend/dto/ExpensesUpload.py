from dataclasses import dataclass


@dataclass
class ExpensesUpload:
    created_expenses: int
    existing_expenses: int