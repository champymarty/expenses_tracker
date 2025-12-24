from dataclasses import dataclass

@dataclass
class SourceDto:
    id: int
    name: str
    type: str
    card_number: str