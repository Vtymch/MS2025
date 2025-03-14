from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from sqlalchemy.orm import Session
from app.database import get_db, engine, get_db_connection, SessionLocal
from app.crud import create_user, get_user, get_users, update_user, delete_user
from app.models import User, Base
import uvicorn
import typer
from rich.console import Console
from rich.table import Table
from app.routers import router  
from prometheus_fastapi_instrumentator import Instrumentator
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create the FastAPI application
app = FastAPI()

# Include routes from the 'router' module
app.include_router(router)

# Enable Prometheus monitoring
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Load environment variables from .env file
load_dotenv()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("app/static/favicon.ico")

# Root page (API home page)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Login page route
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Function to update user data
def update_user_data():
    db = SessionLocal()
    try:
        # Check the number of users
        user_count = db.query(User).count()
        if user_count >= 10000:
            # Delete older users if there are too many
            users_to_delete = db.query(User).order_by(User.updated_at.asc()).limit(user_count - 9999).all()
            for user in users_to_delete:
                db.delete(user)
            db.commit()
        # Update the 'updated_at' timestamp for all users
        db.query(User).update({"updated_at": datetime.now()})
        db.commit()
        print("Updated users data.")
    finally:
        db.close()

# Set up background scheduler to update user data periodically
scheduler = BackgroundScheduler()
scheduler.add_job(update_user_data, 'interval', seconds=10)

# Job listener to handle job execution events
def job_listener(event):
    if event.exception:
        print(f"Job {event.job_id} failed")
    else:
        print(f"Job {event.job_id} succeeded")

# Add job listener to the scheduler
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
scheduler.start()

# API endpoints for user management
@app.post("/users/")
def create_user_api(username: str, email: str, password: str, region: str = None, db: Session = Depends(get_db)):
    return create_user(db=db, username=username, email=email, password=password, region=region)

@app.get("/users/{user_id}")
def get_user_api(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/")
def get_users_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db=db, skip=skip, limit=limit)

@app.put("/users/{user_id}")
def update_user_api(user_id: int, username: str = None, email: str = None, region: str = None, db: Session = Depends(get_db)):
    db_user = update_user(db=db, user_id=user_id, username=username, email=email, region=region)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}")
def delete_user_api(user_id: int, db: Session = Depends(get_db)):
    db_user = delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# WebSocket support for real-time communication
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)

# Typer CLI for command-line interactions
cli = typer.Typer()

# CLI command to list users
@cli.command()
def list_users():
    db = get_db_connection()
    users = get_users(db=db, skip=0, limit=100)
    table = Table(title="User List")
    table.add_column("ID", style="bold")
    table.add_column("Username")
    table.add_column("Region")
    table.add_column("Last Updated")
    
    for user in users:
        table.add_row(str(user.id), user.username, user.region, str(user.updated_at))
    
    console = Console()
    console.print(table)

# CLI command to check server status
@cli.command()
def server_status():
    db = get_db_connection()
    users = get_users(db=db, skip=0, limit=100)
    console = Console()
    console.print(f"Total users: {len(users)}")
    for user in users:
        console.print(f"{user.username} - {user.region}")

# Run the CLI
if __name__ == "__main__":
    typer.run(cli)
