import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
LOG_LEVEL = logging.getLevelName(logging.getLevelNamesMapping()[os.getenv("LOG_LEVEL", "INFO").strip().upper()])
UI_URL = os.getenv("UI_URL", "http://localhost:4200")


DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "expenses_tracker.db")
DB_SQL_EXPORT_PATH = os.path.join(DATA_DIR, "exported_expenses_tracker.sql")
SQL_INIT_SCRIPT_PATH = os.path.join(DATA_DIR, "init_db.sql")
SQL_INIT_DATA_PATH = "init_data.txt"

if os.path.isdir(DATA_DIR) is False:
    os.makedirs(DATA_DIR)



# Configure logging
def configure_logging():
    """Configure logging with LOG_LEVEL environment variable"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Suppress verbose SQLAlchemy logs
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

configure_logging()
logger = logging.getLogger(__name__)
logger.info(f"Environment: {ENVIRONMENT}, UI_URL: {UI_URL}, LOG_LEVEL: {LOG_LEVEL}")
logger.info(f"Database path: {DB_PATH}")
