from dataclasses import dataclass, field

from dto.FileFailedToExtract import FileFailedToExtract


@dataclass
class ExpensesUpload:
    created_expenses: int
    existing_expenses: int
    filesFailedToExtract: list[FileFailedToExtract] = field(default_factory=list)