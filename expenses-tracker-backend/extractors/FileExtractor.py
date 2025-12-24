from abc import abstractmethod
from fastapi import UploadFile

from DatabaseSetup import SESSION_MAKER
from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload
from sqlalchemy.orm import Session


class FileExtractor:
    def __init__(self, file: UploadFile, source: Source):
        self.file = file
        self.source = source

    @abstractmethod
    async def extract(self) -> ExpensesUpload:
        """Extracts the content of the file."""
        pass

    @abstractmethod
    async def apply(self) -> bool:
        """Extracts the content of the file."""
        pass

    def get_sources(self, type: str) -> list[Source]:
        if self.source is None:
            with SESSION_MAKER() as session:
                session: Session
                return session.query(Source).filter(Source.type == type).all()
        else:
            return [self.source]