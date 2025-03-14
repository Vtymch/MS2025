from sqlalchemy.orm import Session
from app.models import User
from datetime import datetime
from app.security import hash_password, verify_password  # Import functions for hashing and verifying passwords

# Create a new user
def create_user(db: Session, username: str, email: str, password: str, region: str = None):
    hashed_password = hash_password(password)  # Hash the password
    db_user = User(username=username, email=email, password=hashed_password, region=region, updated_at=datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get a user by ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Get all users with optional pagination
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# Update user data
def update_user(db: Session, user_id: int, username: str = None, email: str = None, region: str = None):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        if username:
            db_user.username = username
        if email:
            db_user.email = email
        if region:
            db_user.region = region
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
    return db_user

# Delete a user
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# Verify user password during login
def verify_user_password(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):  # Verify the password
        return user
    return None
