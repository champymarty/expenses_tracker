from fastapi import FastAPI
from app.routers import Expenses
from app.routers import Budget
from app.routers import CategoryFamily
from app.routers import Category
from app.routers import Source
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Expense Tracker API",
    description="Upload Excel files to load expenses.",
    version="1.0.0"
)

app.include_router(Expenses.router)
app.include_router(Budget.router)
app.include_router(CategoryFamily.router)
app.include_router(Category.router)
app.include_router(Source.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    

