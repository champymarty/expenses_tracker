from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from database.Models import *
import re

def regexp(expr, item):
    reg = re.compile(expr, re.IGNORECASE)
    return reg.search(item) is not None


engine = create_engine('sqlite:///expenses_tracker.db')
SESSION_MAKER: sessionmaker = sessionmaker(bind=engine)

@event.listens_for(engine, "connect")
def setup_regexp(dbapi_connection, connection_record):
    dbapi_connection.create_function("REGEXP", 2, regexp)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)