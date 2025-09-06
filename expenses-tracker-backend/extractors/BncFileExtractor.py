import pandas as pd
from database.Facades.ExpenseFacade import ExpenseFacade
from dto.ExpensesUpload import ExpensesUpload
from extractors.FileExtractor import FileExtractor
from DatabaseSetup import SESSION_MAKER
from sqlalchemy.orm import Session

from datetime import datetime


class BncFileExtractor(FileExtractor):
    """
    Extracts content from a BNC Excel file.
    """

    BNC_HEADERS = [
        "Date", "Card Number", "Description", "Category", "Debit", "Credit"
    ]

    def extract(self) -> ExpensesUpload:
        """
        Extracts the content of the BNC Excel file.
        """
        # Implement the extraction logic specific to BNC Excel files
        # For example, reading the file and processing its content
        df = pd.read_csv(self.file.file, sep=';', names=BncFileExtractor.BNC_HEADERS, header=0)
        created_count = 0
        existing_expenses = 0
        with SESSION_MAKER() as session:
            session: Session
            expenseFacade = ExpenseFacade(session)
            for _, row in df.iterrows():
                # Assuming the BNC file has the following columns:
                # Date, Card Number, Description, Category, Debit, Credit
                amount = row["Debit"]
                if not row["Debit"]:
                    amount = -row["Credit"]
                created_expense = expenseFacade.create_expense(
                    description=row["Description"],
                    amount=amount,
                    date=datetime.strptime(row["Date"], "%Y-%m-%d"),
                    category_name=row["Category"],
                    source_id=self.source.id
                )
                if created_expense is not None:
                    created_count += 1
                else:
                    existing_expenses += 1
            session.commit()
        return ExpensesUpload(created_count, existing_expenses)
