import datetime
import logging
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from config import DB_PATH, DB_SQL_EXPORT_PATH, SQL_INIT_SCRIPT_PATH
from database.Models import *
import re

logger = logging.getLogger(__name__)

def regexp(expr, item):
    reg = re.compile(expr, re.IGNORECASE)
    return reg.search(item) is not None


ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SESSION_MAKER: sessionmaker = sessionmaker(bind=ENGINE)

@event.listens_for(ENGINE, "connect")
def setup_regexp(dbapi_connection, connection_record):
    dbapi_connection.create_function("REGEXP", 2, regexp)

def export_database() -> str:
    with ENGINE.connect() as connection:
        dbapi_conn = connection.connection
        # Use another context manager to open the output file in write mode
        with open(DB_SQL_EXPORT_PATH, 'w') as f:
            # Iterate over the dump lines and write to the file
            for line in dbapi_conn.iterdump():
                f.write(f'{line}\n')
    return DB_SQL_EXPORT_PATH

logger.info("Database engine and session maker initialized.")

if os.path.exists(SQL_INIT_SCRIPT_PATH):
    logger.info(f"Database init file found at {SQL_INIT_SCRIPT_PATH}.")
    with ENGINE.connect() as connection:
        with open(SQL_INIT_SCRIPT_PATH, 'r') as f:
            init_sql = f.read()
            dbapi_conn = connection.connection
            try:
                dbapi_conn.executescript(init_sql)
            except AttributeError:
                logger.warning("executescript not available, executing statements individually.")
                for statement in init_sql.split(';'):
                    stmt = statement.strip()
                    if stmt:
                        connection.execute(text(stmt))
    logger.info("Database initialized using init script.")

    logger.info("Renaming init script to avoid re-initialization on next startup.")
    os.rename(SQL_INIT_SCRIPT_PATH, f"{SQL_INIT_SCRIPT_PATH}.processed_at_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
else:
    logger.info("No database init file found; skipping initialization.")

