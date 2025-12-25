from datetime import datetime
import logging
from bs4 import BeautifulSoup
from fastapi import UploadFile
from DatabaseSetup import SESSION_MAKER
from sqlalchemy.orm import Session
from database.Facades.ExpenseFacade import ExpenseFacade
from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload
from dto.FileFailedToExtract import FileFailedToExtract
from extractors.FileExtractor import FileExtractor


class HtmlRogerExtractor(FileExtractor):
    """
    Extracts content from an HTML file from Roger.
    """

    SEPERATOR = ";"
    SOURCE_TYPE = "ROGER"

    IMG_HEADER_ALT_TEXT = ["Rogers bank logo", "Logo de la Banque Rogers"]

    def __init__(self, file: UploadFile, source: Source):
        super().__init__(file, source)
        self.LOGGER = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    async def apply(self) -> bool:
        """Validates if the file is an HTML file from Roger."""
        self.LOGGER.info(f"Applying HTML Roger file extractor on file {self.file.filename}")

        if self.file.filename is None:
            self.LOGGER.info("File has no filename.")
            return False
        
        if not self.file.filename.lower().endswith('.html') and not self.file.filename.lower().endswith('.htm'):
            self.LOGGER.info("File is not an HTML file based on extension.")
            return False
        
        try:
            html_bytes = await self.file.read()
            html_str = html_bytes.decode("utf-8")
            soup = BeautifulSoup(html_str, 'html.parser')
            # Simple validation: check for a specific element or text unique to Roger HTML files
            if all(soup.find("img", attrs={"alt": alt_text}) is None for alt_text in self.IMG_HEADER_ALT_TEXT):
                self.LOGGER.info("HTML structure does not match expected Roger format.")
                return False
            self.LOGGER.info("HTML Roger file format validated successfully.")
            return True
        except Exception as e:
            self.LOGGER.error(f"Error reading HTML file: {str(e)}")
            return False
        finally:
            await self.file.seek(0)  # Reset file pointer after reading

    async def extract(self) -> ExpensesUpload:
        """
        Extracts the content of the HTML file.
        """
        expensesUpload = ExpensesUpload(0, 0)
    
        html_bytes = await self.file.read()
        html_str = html_bytes.decode("utf-8")
        
        soup = BeautifulSoup(html_str, 'html.parser')
        
        # Example: Extract the title of the HTML page
        all_tbody = soup.find_all('tbody')
        posted_transactions_tbody = None
        if len(all_tbody) == 2:
            posted_transactions_tbody = all_tbody[1]
        elif len(all_tbody) == 1:
            posted_transactions_tbody = all_tbody[0]
        else:
            expensesUpload.filesFailedToExtract.append(
                FileFailedToExtract(self.file.filename, "Posted Transactions table not found in HTML file.") # type: ignore
            )
            self.LOGGER.warning("Posted Transactions table not found in HTML file.")
            return expensesUpload
        all_tr = posted_transactions_tbody.find_all('tr')

        card_holder_p = soup.find_all("p", attrs={"aria-label": "Selected cardholder"})
        card_number = None
        if card_holder_p and len(card_holder_p) > 0:
            card_number = card_holder_p[0].get_text().strip().split(" ")[-1].replace(".", "")
        if card_number is None:
            expensesUpload.filesFailedToExtract.append(
                FileFailedToExtract(self.file.filename, "Card number not found in HTML file.") # type: ignore
            )
            return expensesUpload

        self.LOGGER.info(f"Extracting expenses from HTML Roger file: {self.file.filename} for card number: {card_number}")

        sources = self.get_sources(HtmlRogerExtractor.SOURCE_TYPE)
        matching_sources = [s for s in sources if s.card_number == card_number]
        if len(matching_sources) == 0:
            expensesUpload.filesFailedToExtract.append(
                FileFailedToExtract(self.file.filename, f"No matching source found for card number {card_number}.") # type: ignore
            )
            self.LOGGER.warning(f"No matching source found for card number {card_number}.")
            return expensesUpload
        
        self.source = matching_sources[0]
        self.LOGGER.info(f"Using source {self.source.name} for extraction.")

        with SESSION_MAKER() as session:
            session: Session
            expenseFacade = ExpenseFacade(session)
            for tr in all_tr[1:]:
                line = tr.get_text(separator=HtmlRogerExtractor.SEPERATOR).strip()
                data = line.split(HtmlRogerExtractor.SEPERATOR)
                if len(data) != 7:
                    raise ValueError(f"Invalid number of columns in HTML row: {line}")
                date, _, description, category, _, amount, _ = data
                date  = datetime.strptime(date.strip(), "%b %d, %Y")
                description = description.strip()
                category = category.strip()
                amount = float(amount.replace("$", "").replace(",", "").replace(" ", "").strip())
                created_expense = expenseFacade.create_expense(
                    description=description,
                    amount=amount,
                    date=date,
                    category_name=category,
                    source_id=self.source.id
                )
                if created_expense is not None:
                    expensesUpload.created_expenses += 1
                    self.LOGGER.info(f"Created expense. Date: {date}, Description: {description}, Category: {category}, Amount: {amount}")
                else:
                    expensesUpload.existing_expenses += 1
                    self.LOGGER.info(f"Expense already exist. Date: {date}, Description: {description}, Category: {category}, Amount: {amount}")
            session.commit()
        return expensesUpload