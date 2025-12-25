import logging
from fastapi import UploadFile
import pandas as pd
from database.Facades.ExpenseFacade import ExpenseFacade
from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload
from DatabaseSetup import SESSION_MAKER
from sqlalchemy.orm import Session

from datetime import datetime

from extractors.excel.ExcelFileExtractor import ExcelFileExtractor

LOGGER = logging.getLogger(f'{__file__}')


class BncFileExtractor(ExcelFileExtractor):
    """
    Extracts content from a BNC Excel file.
    """

    BNC_SOURCE_NAME = "BNC"

    BNC_HEADERS = [
        "Date", "card Number", "Description", "Category", "Debit", "Credit"
    ]

    def __init__(self, file: UploadFile, source: Source):
        super().__init__(file, source)
        self.LOGGER = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    async def apply(self) -> bool:
        """Extracts the content of the file."""
        self.LOGGER.info(f"Applying BNC file extractor on file {self.file.filename}")
        isExcelFile = await super().apply()
        if not isExcelFile:
            return False
        try:
            # Read first few rows to validate file format
            df = pd.read_csv(self.file.file, sep=';', nrows=2)
            
            # Verify if required headers are present
            file_headers = set(df.columns)
            required_headers = set(self.BNC_HEADERS)
            
            if not required_headers.issubset(file_headers):
                missing_headers = required_headers - file_headers
                self.LOGGER.info(f"Missing required headers: {missing_headers}. File headers: {file_headers}")
                return False

            self.LOGGER.info("BNC file format validated successfully.")    
            return True
        except Exception as e:
            self.LOGGER.error(f"Error reading file: {str(e)}")
            return False
        finally:
            self.file.file.seek(0)  # Reset file pointer after reading
        
    async def extract(self) -> ExpensesUpload:
        """
        Extracts the content of the BNC Excel file.
        """
        # Implement the extraction logic specific to BNC Excel files
        # For example, reading the file and processing its content
        sources = self.get_sources(BncFileExtractor.BNC_SOURCE_NAME)
        self.LOGGER.info(f"Extracting expenses from BNC file: {self.file.filename} using sources: {[s.name for s in sources]}")

        df = pd.read_csv(self.file.file, sep=';', names=BncFileExtractor.BNC_HEADERS, header=0)
        self.LOGGER.info(f"Extracting expenses from BNC file with {df}")
        created_count = 0
        existing_expenses = 0
        with SESSION_MAKER() as session:
            session: Session
            expenseFacade = ExpenseFacade(session)
            for _, row in df.iterrows():
                # Assuming the BNC file has the following columns:
                # Date, Card Number, Description, Category, Debit, Credit
                LOGGER.debug(f"Processing row: {row}")
                if pd.isna(row["Description"]) or pd.isna(row["Date"]) or pd.isna(row["card Number"]):
                    self.LOGGER.warning(f"Skipping row with missing Description or Date: {row}")
                    continue
                amount = row["Debit"]
                card_number: str = row["card Number"].strip().replace("*", "")
                row_source = None
                if self.source is None:
                    matching_sources = [s for s in sources if s.card_number == card_number]
                    if not matching_sources:
                        self.LOGGER.warning(f"No matching source found for card number {card_number}. Skipping row.")
                        raise ValueError(f"No matching source found for card number {card_number}")
                    row_source = matching_sources[0]
                else:
                    row_source = self.source

                if not row["Debit"]:
                    amount = -row["Credit"]
                created_expense = expenseFacade.create_expense(
                    description=row["Description"],
                    amount=amount,
                    date=datetime.strptime(row["Date"], "%Y-%m-%d"),
                    category_name=row["Category"],
                    source_id=row_source.id
                )
                if created_expense is not None:
                    created_count += 1
                else:
                    existing_expenses += 1
            session.commit()
        return ExpensesUpload(created_count, existing_expenses)
