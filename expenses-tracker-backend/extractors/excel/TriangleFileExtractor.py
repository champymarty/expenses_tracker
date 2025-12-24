import logging
from fastapi import UploadFile
import pandas as pd
from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload
from dto.FileFailedToExtract import FileFailedToExtract
from extractors.FileExtractor import FileExtractor
from database.Facades.ExpenseFacade import ExpenseFacade
from DatabaseSetup import SESSION_MAKER
from datetime import datetime
from sqlalchemy.orm import Session

class TriangleFileExtractor(FileExtractor):
    """
    Extracts content from a Triangle CSV file.
    """

    HEADERS = [
        "REF", "TRANSACTION DATE", "POSTED DATE", "TYPE", "DESCRIPTION", 
        "Category", "AMOUNT"
    ]

    COLUMN_TYPES: dict = {
        "REF": pd.StringDtype(),
        "TRANSACTION DATE": pd.StringDtype(),
        "POSTED DATE": pd.StringDtype(),
        "TYPE": pd.StringDtype(),
        "DESCRIPTION": pd.StringDtype(),
        "Category": pd.StringDtype(),
        "AMOUNT": pd.Float64Dtype()
    }

    SOURCE_TYPE = "TRIANGLE"

    def __init__(self, file: UploadFile, source: Source):
        super().__init__(file, source)
        self.LOGGER = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    async def apply(self) -> bool:
        """Extracts the content of the file."""
        self.LOGGER.info(f"Applying Triangle file extractor on file {self.file.filename}")
        try:
            # Read first few rows to validate file format
            df = pd.read_csv(self.file.file, sep=',', nrows=2, skiprows=3)
            
            # Verify if required headers are present
            file_headers = set(df.columns)
            required_headers = set(TriangleFileExtractor.HEADERS)
            
            if not required_headers.issubset(file_headers):
                missing_headers = required_headers - file_headers
                self.LOGGER.info(f"Missing required headers: {missing_headers}. File headers: {file_headers}")
                return False

            self.LOGGER.info("Triangle file format validated successfully.")    
            return True
        except Exception as e:
            self.LOGGER.error(f"Error reading file: {str(e)}")
            return False
        finally:
            self.file.file.seek(0)  # Reset file pointer after reading

    async def extract(self) -> ExpensesUpload:
        """
        Extracts the content of the Triangle CSV file.
        """
        self.LOGGER.info(f"Extracting Triangle file: {self.file.filename}")

        sources = self.get_sources(TriangleFileExtractor.SOURCE_TYPE)
        if len(sources) == 0:
            self.LOGGER.error(f"No source found for type {TriangleFileExtractor.SOURCE_TYPE}")
            return ExpensesUpload(0, 0, [FileFailedToExtract(self.file.filename, f"No source found for type {TriangleFileExtractor.SOURCE_TYPE}")]) # type: ignore
        if len(sources) > 1:
            # Card number is not available in Triangle files, so we cannot disambiguate sources
            self.LOGGER.warning(f"Multiple sources found for type {TriangleFileExtractor.SOURCE_TYPE}")
            return ExpensesUpload(0, 0, [FileFailedToExtract(self.file.filename, f"Multiple sources found for type {TriangleFileExtractor.SOURCE_TYPE}. No card number in triangle excel download")]) # type: ignore
        self.source = sources[0]

        # Skip the first 4 lines (header information)
        df = pd.read_csv(self.file.file, sep=',', dtype=TriangleFileExtractor.COLUMN_TYPES, 
                        skiprows=4, names=TriangleFileExtractor.HEADERS)
        
        created_count = 0
        existing_expenses = 0

        with SESSION_MAKER() as session:
            session: Session
            expenseFacade = ExpenseFacade(session)
            
            for _, row in df.iterrows():
                self.LOGGER.debug(f"Processing row: {row}")
                                
                category: str | None = row["Category"]
                if category is None or pd.isna(category) or category.strip() == "":
                    category = "Uncategorized"

                created_expense = expenseFacade.create_expense(
                    description=row["DESCRIPTION"],
                    amount=float(row["AMOUNT"]),
                    date=datetime.strptime(row["TRANSACTION DATE"], "%Y-%m-%d"),
                    category_name=category,
                    source_id=self.source.id
                )
                
                if created_expense is not None:
                    created_count += 1
                else:
                    existing_expenses += 1
                    
            session.commit()
            
        return ExpensesUpload(created_count, existing_expenses)