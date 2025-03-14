from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from app import models, schemas
from app.database import SessionLocal
from app.config import settings

# Create an instance of CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for signing JWT tokens and the algorithm
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str):
    """Hashes a password"""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Verifies the password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT token with an expiration time"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes the JWT token and checks its validity"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_user(db: Session, username: str):
    """Gets a user from the database by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def register_user(db: Session, username: str, password: str) -> bool:
    """Adds a new user to the database"""
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return False  # User already exists
    new_user = models.User(username=username, hashed_password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    return True

def authenticate_user(db: Session, username: str, password: str) -> Optional[str]:
    """Authenticates the user and issues a JWT token"""
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None  # Invalid credentials
    access_token = create_access_token({"sub": username})
    return access_token
