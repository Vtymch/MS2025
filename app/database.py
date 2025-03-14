from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from app.config import settings

# Load environment variables
load_dotenv()

# Set up the database URL from environment variables or .env file
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

if not DATABASE_URL:
    # Default PostgreSQL URL if no environment variable is provided
    DATABASE_URL = "postgresql://postgres:MS2025@Secure!@localhost:5432/master_db"

# Create a database engine
engine = create_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20)

# Create a session maker to handle database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a base class for all models
Base = declarative_base()

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db  # Yield the session for use in CRUD operations
    finally:
        db.close()  # Close the session after use

# Function to get a direct database connection (optional use case)
def get_db_connection():
    db = engine.connect()
    try:
        yield db  # Yield the connection for use
    finally:
        db.close()  # Close the connection after use

# Create all tables in the database if they are not already created
Base.metadata.create_all(bind=engine)

