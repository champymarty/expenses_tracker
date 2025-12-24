from dataclasses import dataclass


@dataclass
class FileFailedToExtract:
    filename: str
    reason: str