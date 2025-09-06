from dataclasses import dataclass

from dto.CategoryDTO import CategoryDto

@dataclass
class CombineCategoryFamilyDto:
    surviving_cateogy_family_id: int
    deleting_cateogy_family_id: int
    name: str