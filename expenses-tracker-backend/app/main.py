import logging
import os
from fastapi import FastAPI
from app.routers import Expenses
from app.routers import Budget
from app.routers import CategoryFamily
from app.routers import Category
from app.routers import Source
from fastapi.middleware.cors import CORSMiddleware

# Get environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
UI_URLS = os.getenv("UI_URLS", "http://localhost:4200")

app = FastAPI(
    title="Expense Tracker API",
    description="Upload Excel files to load expenses.",
    version="1.0.0"
)

# Allow automatic trailing-slash redirects so routes like /api/category-family redirect to /api/category-family/
app.router.redirect_slashes = True

# Configure CORS
# In development allow any origin to simplify local testing;
# in production parse the UI_URLS environment variable.
if ENVIRONMENT == "dev":
    allow_origins = ["*"]
else:
    allow_origins = [u.strip() for u in UI_URLS.split(",")]

LOGGER = logging.getLogger(__file__)

LOGGER.info(f"Configuring CORS with allowed origins: {allow_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

app.include_router(Expenses.router, prefix=API_PREFIX)
app.include_router(Source.router, prefix=API_PREFIX)
app.include_router(Budget.router, prefix=API_PREFIX)
app.include_router(CategoryFamily.router, prefix=API_PREFIX)
app.include_router(Category.router, prefix=API_PREFIX)
    

