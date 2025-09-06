from dataclasses import dataclass


@dataclass
class CategoryDto:
    id: int | None
    name: str
    category_family_id: int