from dataclasses import dataclass

from database.Source import Source

@dataclass
class SourceAverage:
    source: Source
    average: float