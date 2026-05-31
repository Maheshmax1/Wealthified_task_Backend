from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine

# Import our different API routes (endpoints)
from router.dashboard import router as dashboard_router
from router.investors import router as investors_router
from router.mutual_funds import router as mutual_funds_router
from router.transactions import router as transactions_router

# This line automatically creates the database tables if they don't exist yet
Base.metadata.create_all(bind=engine)

# Create the main FastAPI application object
app = FastAPI(
    title="Mutual Fund Dashboard API",
    description="API for mutual fund transaction analytics",
    version="1.0.0",
)

# CORS middleware allows our React frontend (running on a different port) 
# to talk to this FastAPI backend without getting security errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow requests from any origin (e.g., localhost:5173)
    allow_credentials=True,
    allow_methods=["*"], # Allow all types of requests (GET, POST, etc.)
    allow_headers=["*"],
)

# Connect our imported routes to the main app
app.include_router(dashboard_router)
app.include_router(investors_router)
app.include_router(mutual_funds_router)
app.include_router(transactions_router)

# This is a simple route that responds when you visit the root URL (http://localhost:8000/)
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to the Mutual Fund Dashboard API!",
        "docs": "Visit /docs to see the interactive API documentation",
        "endpoints": {
            "investor_purchases": "/api/dashboard/investor-purchases",
            "fund_purchases": "/api/dashboard/fund-purchases",
            "investors": "/api/dashboard/investors",
            "funds_summary": "/api/dashboard/funds/summary",
        },
    }

# A simple health check route to make sure the server is running correctly
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}