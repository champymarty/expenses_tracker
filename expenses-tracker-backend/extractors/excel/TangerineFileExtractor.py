import logging
import re
from fastapi import UploadFile
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from database.Facades.ExpenseFacade import ExpenseFacade
from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload
from extractors.FileExtractor import FileExtractor
from DatabaseSetup import SESSION_MAKER


class TangerineFileExtractor(FileExtractor):
    """
    Extracts content from a Tangerine card CSV file with columns:
    Date de l'opération,Transaction,Nom,Description,Montant
    """

    COLUMN_TYPES: dict = {
        "Date de l'opération": pd.StringDtype(),
        "Transaction": pd.StringDtype(),
        "Nom": pd.StringDtype(),
        "Description": pd.StringDtype(),
        "Montant": pd.StringDtype()  # parse manually to handle signs/formatting
    }

    SOURCE_TYPE = "TANGERINE"

    def __init__(self, file: UploadFile, source: Source):
        super().__init__(file, source)
        self.LOGGER = logging.getLogger(f'{__name__}.{self.__class__.__name__}')


    def find_col(self, df: pd.DataFrame, possible_names) -> str:
        for n in possible_names:
            if n in df.columns:
                return n
        raise Exception(f"None of the possible column names found for: {possible_names}")
    
    async def apply(self) -> bool:
        """Extracts the content of the Tangerine CSV file."""
        self.LOGGER.info(f"Applying Tangerine file extractor on file {self.file.filename}")
        try:
            # Read first few rows to validate file format
            df = pd.read_csv(self.file.file, sep=',', nrows=2)
            
            # Verify if required headers are present
            file_headers = set(df.columns)
            required_headers = {
                "Date de l'opération", "Transaction", "Nom", "Description", "Montant"
            }
            
            if not required_headers.issubset(file_headers):
                missing_headers = required_headers - file_headers
                self.LOGGER.info(f"Missing required headers: {missing_headers}. File headers: {file_headers}")
                return False

            self.LOGGER.info("Tangerine file format validated successfully.")    
            return True
        except Exception as e:
            self.LOGGER.error(f"Error reading file: {str(e)}")
            return False
        finally:
            self.file.file.seek(0)  # Reset file pointer for future reads

    async def extract(self) -> ExpensesUpload:
        self.LOGGER.info(f"Extracting Tangerine file: {self.file.filename}")

        sources = self.get_sources(TangerineFileExtractor.SOURCE_TYPE)
        if len(sources) == 0:
            self.LOGGER.error(f"No source found for type {TangerineFileExtractor.SOURCE_TYPE}")
            return ExpensesUpload(0, 0, [FileFailedToExtract(self.file.filename, "No source found for type {TriangleFileExtractor.SOURCE_TYPE}")]) # type: ignore
        if len(sources) > 1:
            # Card number is not available in Triangle files, so we cannot disambiguate sources
            self.LOGGER.warning(f"Multiple sources found for type {TangerineFileExtractor.SOURCE_TYPE}")
            return ExpensesUpload(0, 0, [FileFailedToExtract(self.file.filename, f"Multiple sources found for type {TangerineFileExtractor.SOURCE_TYPE}. No card number in tangerine excel download")]) # type: ignore
        self.source = sources[0]

        df = pd.read_csv(
            self.file.file,
            sep=',',
            dtype=TangerineFileExtractor.COLUMN_TYPES,
            header=0,
            encoding='latin-1'
        )

        date_col = self.find_col(df, ["Date de l'opération", "Date de l'operation", "Date", "Date de l'opÃ©ration"])
        name_col = self.find_col(df, ["Nom", "Name", "Merchant"])
        desc_col = self.find_col(df, ["Description", "Description "])
        amount_col = self.find_col(df, ["Montant", "Amount", "AMOUNT"])

        created_count = 0
        existing_expenses = 0

        with SESSION_MAKER() as session:
            session: Session
            expenseFacade = ExpenseFacade(session)

            for _, row in df.iterrows():
                self.LOGGER.debug("Processing row: %s", row)

                # parse date
                date_str = str(row[date_col]) if date_col is not None else ""
                try:
                    date = datetime.strptime(date_str.strip(), "%m/%d/%Y")
                except Exception:
                    # fallback: try ISO or empty -> skip
                    try:
                        date = datetime.fromisoformat(date_str.strip())
                    except Exception:
                        self.LOGGER.warning("Unable to parse date '%s', skipping row", date_str)
                        continue

                # parse amount (handle currency symbols, thousands separators)
                raw_amount = str(row[amount_col]) if amount_col is not None else "0"
                amount_str = raw_amount.replace("$", "").replace(",", "").strip()
                try:
                    amount = float(amount_str) * -1  # Tangerine amounts are negative for expenses
                except Exception:
                    self.LOGGER.warning("Unable to parse amount '%s', skipping row", raw_amount)
                    continue

                # description / merchant name
                merchant = str(row[name_col]).strip()

                # extract category from Description if present (e.g. "... ~ Category: Parking")
                category = "Uncategorized"
                if desc_col is not None:
                    desc = str(row[desc_col]) if not pd.isna(row[desc_col]) else ""
                    # common patterns: "Category: <name>" or "Category : <name>"
                    m = re.search(r"Category\s*[:]\s*([^,~\n\r]+)", desc, flags=re.IGNORECASE)
                    if m:
                        category = m.group(1).strip()
                    else:
                        self.LOGGER.warning("No category found in description '%s', defaulting to 'Uncategorized'", desc)

                created_expense = expenseFacade.create_expense(
                    description=merchant,
                    amount=amount,
                    date=date,
                    category_name=category,
                    source_id=self.source.id
                )

                if created_expense is not None:
                    created_count += 1
                else:
                    existing_expenses += 1

            session.commit()

        return ExpensesUpload(created_count, existing_expenses)