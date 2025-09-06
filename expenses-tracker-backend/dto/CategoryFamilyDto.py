from dataclasses import dataclass

from dto.CategoryDTO import CategoryDto

@dataclass
class CategoryFamilyDto:
    id: int
    name: str
    regex_pattern: str | None = None
    categories: list[CategoryDto] | None = None