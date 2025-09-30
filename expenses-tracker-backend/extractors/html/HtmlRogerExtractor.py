from datetime import datetime
import logging
from bs4 import BeautifulSoup
from fastapi import UploadFile
from DatabaseSetup import SESSION_MAKER
from sqlalchemy.orm import Session
from database.Facades.ExpenseFacade import ExpenseFacade
from database.Source import Source
from dto.ExpensesUpload import ExpensesUpload
from extractors.FileExtractor import FileExtractor


class HtmlRogerExtractor(FileExtractor):
    """
    Extracts content from an HTML file from Roger.
    """

    SEPERATOR = ";"

    def __init__(self, file: UploadFile, source: Source):
        super().__init__(file, source)
        self.LOGGER = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    async def extract(self) -> ExpensesUpload:
        """
        Extracts the content of the HTML file.
        """
        expensesUpload = ExpensesUpload(0, 0)
    
        html_bytes = await self.file.read()
        html_str = html_bytes.decode("utf-8")
        
        soup = BeautifulSoup(html_str, 'html.parser')
        
        # Example: Extract the title of the HTML page
        all_tr = soup.find_all('tr')


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
                amount = float(amount.replace("$", "").replace(",", ".").replace(" ", "").strip())
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