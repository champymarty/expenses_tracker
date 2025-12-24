import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import SQL_INIT_DATA_PATH
from database.Models import *


engine = create_engine('sqlite:///expenses_tracker.db', echo=False)
Base.metadata.create_all(engine)
SessionLocal: sessionmaker = sessionmaker(bind=engine)

logger = logging.getLogger(__name__)

LINE_SEPARATOR = ';'



def create_default_users(session: Session, users: str):
    """Create default users if they do not exist."""
    for username in users.split(LINE_SEPARATOR):
        if not session.query(User).filter_by(username=username).first():
            user = User(username=username)
            session.add(user)
            logger.info(f"Added user: {user.username}")
        else:
            logger.info(f"User already exists: {username}")
    session.commit()
    logger.info("Default users creation complete.")

def create_source(session: Session, source_line: str):
    """Create default sources if they do not exist."""
    source_name, type, card_number = source_line.split(LINE_SEPARATOR)
    if not session.query(Source).filter_by(name=source_name).first():
        source = Source(name=source_name, type=type, card_number=card_number)
        session.add(source)
        session.commit()
        logger.info(f"Added source: {source.name}")
    else:
        logger.info(f"Source already exists: {source_name}")

try:
    with open(SQL_INIT_DATA_PATH, 'r') as file:
        with SessionLocal() as session:
            for index, line in enumerate(file):
                processed_line = line.strip()
                if processed_line == "":
                    continue
                logger.info(f"Processing line {index + 1}: {processed_line}")
                if index == 0:
                    create_default_users(session, processed_line)
                else:
                    create_source(session, processed_line)
    logger.info("Initial data loaded successfully.")

except FileNotFoundError:
    logger.warning(f"Error: The file '{SQL_INIT_DATA_PATH}' was not found. We will not load initial data.")
except Exception as e:
    logger.error(f"An error occurred: {e}")