import logging
from fastapi import UploadFile
import pandas as pd
from database.Facades.ExpenseFacade import ExpenseFacade
from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload
from extractors.FileExtractor import FileExtractor
from DatabaseSetup import SESSION_MAKER
from sqlalchemy.orm import Session

from datetime import datetime


class RogerFileExtractor(FileExtractor):
    """
    Extracts content from a BNC Excel file.
    """

    HEADERS = [
        "Date", "Posted Date", "Reference Number", "Activity Type", "Activity Status", "Card Number", "Merchant Category Description", 
        "Merchant Name", "Merchant City", "Merchant State or Province", "Merchant Country Code", "Merchant Postal Code", "Amount", "Rewards", "Name on Card"
    ]

    COLUMN_TYPES: dict = {
        "Date": pd.StringDtype(),
        "Posted Date": pd.StringDtype(),
        "Reference Number": float,
        "Activity Type": pd.StringDtype(),
        "Activity Status": pd.StringDtype(),
        "Card Number": pd.StringDtype(),
        "Merchant Category Description": pd.StringDtype(), 
        "Merchant Name": pd.StringDtype(),
        "Merchant City": pd.StringDtype(),
        "Merchant State or Province": pd.StringDtype(),
        "Merchant Country Code": pd.StringDtype(),
        "Merchant Postal Code": pd.StringDtype(),
        "Amount": pd.StringDtype(),
        "Rewards": pd.StringDtype(),
        "Name on Card": pd.StringDtype()
}

    def __init__(self, file: UploadFile, source: Source):
        super().__init__(file, source)
        self.LOGGER = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    async def extract(self) -> ExpensesUpload:
        """
        Extracts the content of the BNC Excel file.
        """
        # Implement the extraction logic specific to BNC Excel files
        # For example, reading the file and processing its content
        df = pd.read_csv(self.file.file, sep=',', dtype=RogerFileExtractor.COLUMN_TYPES, header=0)
        created_count = 0
        existing_expenses = 0
        with SESSION_MAKER() as session:
            session: Session
            expenseFacade = ExpenseFacade(session)
            for _, row in df.iterrows():
                self.LOGGER.debug(f"Processing row: {row}")

                amount_str = str(row["Amount"]).replace("$", "").replace(",", "").strip()
                
                category: str | None = row["Merchant Category Description"]
                if category is None or pd.isna(category) or category.strip() == "":
                    category = "Uncategorized"

                created_expense = expenseFacade.create_expense(
                    description=row["Merchant Name"],
                    amount=float(amount_str),
                    date=datetime.strptime(row["Date"], "%Y-%m-%d"),
                    category_name=category,
                    source_id=self.source.id
                )
                if created_expense is not None:
                    created_count += 1
                else:
                    existing_expenses += 1
            session.commit()
        return ExpensesUpload(created_count, existing_expenses)
