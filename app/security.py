from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import config, models, database

# Create an object for working with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Functions for password hashing
def hash_password(password: str) -> str:
    """Hashes the password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies the password by comparing it with the hashed value."""
    return pwd_context.verify(plain_password, hashed_password)

# OAuth2 scheme for obtaining tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get a database session
def get_db():
    """Creates and yields a database session."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to verify JWT token and extract user information
def verify_token(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    """Verifies the token and retrieves user information."""
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        token_data = models.User(username=username)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return token_data

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    """Creates a JWT token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
    return encoded_jwt

# Function to register a new user
def register_user(db, username: str, password: str) -> bool:
    """Adds a new user to the database."""
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return False  # User already exists
    hashed_password = hash_password(password)
    new_user = models.User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return True

# Function to authenticate a user
def authenticate_user(db, username: str, password: str):
    """Verifies the user and returns a JWT token."""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None  # Invalid credentials
    access_token = create_access_token({"sub": username})
    return access_token
