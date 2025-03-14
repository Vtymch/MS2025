import asyncio
import json
import logging
import socket
import subprocess
import threading
import requests
import tkinter as tk
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from jose import JWTError, jwt

# Logging configuration
logging.basicConfig(filename="server_monitor.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Database configuration
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT configuration
SECRET_KEY = "secret"  # Replace with a secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model for the database
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

Base.metadata.create_all(bind=engine)

# User management functions
def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db, username: str, password: str, role: str = "user"):
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    if expires_delta:
        expiration = datetime.utcnow() + expires_delta
    else:
        expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = data.copy()
    to_encode.update({"exp": expiration})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Load list of servers
try:
    with open("servers.json", "r") as f:
        servers = json.load(f)
except FileNotFoundError:
    servers = []

# Save server list to a file
def save_servers():
    with open("servers.json", "w") as f:
        json.dump(servers, f, indent=4)

# Function to check if a server is reachable via ping
def check_ping(host):
    try:
        output = subprocess.run(["ping", "-n", "1", host], capture_output=True, text=True)
        return "TTL=" in output.stdout
    except Exception as e:
        logging.error(f"Ping error for {host}: {e}")
        return False

# Function to check if a server is accessible via HTTP
def check_http(host):
    try:
        response = requests.get(f"http://{host}", timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"HTTP check error for {host}: {e}")
        return False

# Function to check if a server is accessible via TCP
def check_tcp(host, port):
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except Exception as e:
        logging.error(f"TCP check error for {host}:{port}: {e}")
        return False

# Asynchronous server monitoring function
async def monitor():
    while True:
        for server in servers:
            host = server["host"]
            method = server.get("method", "ping")
            port = server.get("port", 80)
            status = False
            
            # Check server status based on selected method (ping, http, tcp)
            if method == "ping":
                status = check_ping(host)
            elif method == "http":
                status = check_http(host)
            elif method == "tcp":
                status = check_tcp(host, port)
            
            server["status"] = "UP" if status else "DOWN"
            log_entry = f"{host} ({method}) is {'UP' if status else 'DOWN'}"
            print(log_entry)
            logging.info(log_entry)
            
            if not status:
                send_alert(host, method)
        
        save_servers()  # Save the server list to the file
        await asyncio.sleep(10)

# Function to send alerts when a server goes down
def send_alert(host, method):
    print(f"ALERT! {host} ({method}) is DOWN!")

# FastAPI application setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User registration and token models
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def root():
    return {"message": "Server Monitor API is running"}

# User registration endpoint
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = create_user(db, user.username, user.password)
    logging.info(f"User registered: {user.username}")
    return {"username": new_user.username}

# User login endpoint with JWT creation
@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "exp": datetime.utcnow()})
    logging.info(f"User logged in: {user.username}")
    return {"access_token": token, "token_type": "bearer"}

# WebSocket to notify clients of server status
clients = []
async def notify_clients():
    while True:
        servers_data = json.dumps(servers)
        for client in clients:
            try:
                await client.send_text(servers_data)
            except Exception:
                clients.remove(client)
        await asyncio.sleep(5)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        clients.remove(websocket)

# Tkinter GUI for server monitoring
class ServerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Monitor")
        self.server_list = tk.Listbox(root)
        self.server_list.pack()
        self.update_servers()
    
    def update_servers(self):
        # Update server status in Tkinter Listbox
        self.server_list.delete(0, tk.END)
        for server in servers:
            self.server_list.insert(tk.END, f"{server['host']} - {server['method']} - {server['status']}")
        self.root.after(5000, self.update_servers)  # Update every 5 seconds

# Function to run FastAPI server
def start_fastapi():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Function to start Tkinter GUI
def start_gui():
    root = tk.Tk()
    app = ServerMonitorApp(root)
    root.mainloop()

# Function to start server monitoring
def run_monitor():
    import asyncio
    asyncio.run(monitor())  # Start server monitoring

if __name__ == "__main__":
    threading.Thread(target=start_fastapi, daemon=True).start()  # Start FastAPI in a separate thread
    threading.Thread(target=run_monitor, daemon=True).start()  # Start server monitoring in a separate thread
    start_gui()  # Start Tkinter GUI in the main thread
