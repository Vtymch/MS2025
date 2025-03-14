import psycopg2
from dotenv import load_dotenv
import os
from fastapi.testclient import TestClient
from .main import app

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:MS2025@Secure!@localhost:5432/master_db")

# Connect to PostgreSQL database
try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")

# Create a test client for FastAPI
client = TestClient(app)

# Test token creation
def test_create_token():
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

# Test fetching current user data
def test_read_users_me():
    token = client.post("/token", data={"username": "testuser", "password": "testpassword"}).json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
