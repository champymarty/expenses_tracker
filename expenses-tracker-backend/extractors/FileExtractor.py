from abc import abstractmethod
from fastapi import UploadFile

from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload


class FileExtractor:
    def __init__(self, file: UploadFile, source: Source):
        self.file = file
        self.source = source

    @abstractmethod
    def extract(self) -> ExpensesUpload:
        """Extracts the content of the file."""
        pass