from datetime import datetime
from fastapi import APIRouter
from typing import Optional

from DatabaseSetup import SESSION_MAKER
from sqlalchemy.orm import Session
from fastapi.params import Query

from database.Facades.SourceFacade import SourceFacade
from database.Source import Source
from dto.SourceDto import SourceDto

router = APIRouter(
    prefix="/source",
    tags=["source"],
    responses={404: {"description": "Not found"}},
)

def serialize_source(source: Source) -> SourceDto:
    return SourceDto(
        id=source.id,
        name=source.name,
        type=source.type,
        card_number=source.card_number
    )

@router.get("/", summary="Get available sources")
async def get_all_sources():
    with SESSION_MAKER() as session:
        session: Session
        sources = session.query(Source).all()
        return [serialize_source(s) for s in sources]
    

@router.get("/averages", summary="Calculate the all the source average for the given interval.")
async def get_source_averages_between_dates(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"), # type: ignore
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format") # type: ignore
):
    print(f"Received request to calculate budget averages between {start_date} and {end_date}")
    start_date_datetime = None
    if start_date:
        start_date_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_datetime = None
    if end_date:
        end_date_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    print(f"Start date: {start_date_datetime}, End date: {end_date_datetime}")

    averages = []
    with SESSION_MAKER() as session:
        session: Session
        expenseFacade = SourceFacade(session)
        averages = expenseFacade.get_average_expense_for_sources(
            start_date=start_date_datetime,
            end_date=end_date_datetime
        )
    return averages