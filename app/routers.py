from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from app.database import SessionLocal
import asyncio
from . import models, schemas, auth, security
from app.database import get_db
from app.update_users import start_updating
from app.auth import register_user, authenticate_user
from app.schemas import UserCreate, Token

def get_db():
    # Creates a new database session and ensures it is closed after use
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

# Starts the process of updating users when the application starts
start_updating()

# Register a new user
@router.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Attempts to register a new user and returns a success message if successful
    if not register_user(db, user.username, user.password):
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "Registration successful"}

# Authenticate user and return JWT token
@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    # Authenticates the user and generates a JWT token if the credentials are correct
    token = authenticate_user(db, user.username, user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": token, "token_type": "bearer"}

# Create a new user in the database
@router.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Adds a new user to the database and returns the user details
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password,
        region=user.region
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get a list of all users
@router.get("/users/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    # Fetches and returns all users from the database
    return db.query(models.User).all()

# Update user data, such as ping values
@router.post("/update_users/")
def update_users(db: Session = Depends(get_db)):
    # Executes an SQL query to update the users' data
    db.execute("UPDATE users_info SET ping = ping + (random() * 20 - 10), updated_at = NOW() WHERE ping IS NOT NULL;")
    db.commit()
    return {"message": "Users updated"}

# WebSocket to send real-time updates to clients
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    while True:
        # Fetches all users and sends their data to the client every 10 seconds
        users = db.query(models.User).all()
        data = [{"id": u.id, "username": u.username, "ping": u.ping, "color": u.get_ping_color()} for u in users]
        await websocket.send_json(data)
        await asyncio.sleep(10)  # Send updates every 10 seconds

# Obtain an access token using a username and password
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Validates user credentials and returns a JWT token
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Get the currently authenticated user
@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(security.verify_token)):
    # Returns the current authenticated user's information
    return current_user
