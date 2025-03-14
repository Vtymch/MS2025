from fastapi import FastAPI
from .routers import router  # Import routes from your routers.py file
from app.database import SessionLocal, engine  # Import database session and engine
from app.models import Base  # Import models for interacting with the database
import os

# Initialize FastAPI application
app = FastAPI()

# Include external routes (from routers.py)
app.include_router(router)

# Database initialization function
def init_db():
    # Create tables in the database if they don't exist
    if not os.path.exists("test.db"):
        Base.metadata.create_all(bind=engine)

# Create tables on app startup
@app.on_event("startup")
def on_startup():
    init_db()

# Route for checking if the API is working
@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

# Additional routes can be added here
