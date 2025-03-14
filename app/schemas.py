from pydantic import BaseModel 

# UserCreate model for creating a new user, with optional region
class UserCreate(BaseModel):
    username: str  # Username of the user
    email: str  # Email address of the user
    password: str  # User's password
    region: str | None = None  # Optional region of the user

# UserResponse model for returning user information
class UserResponse(BaseModel):
    id: int  # User's unique ID
    username: str  # Username of the user
    email: str  # Email address of the user
    is_active: bool  # Whether the user is active
    region: str | None = None  # Optional region of the user

    class Config:
        from_attributes = True  # Enable mapping from attributes

# Token model to represent JWT access token and token type
class Token(BaseModel):
    access_token: str  # JWT access token
    token_type: str  # Type of the token (e.g., "bearer")

# Base user model with just the username
class UserBase(BaseModel):
    username: str  # Username of the user

# User model with additional fields like ID, for ORM compatibility
class User(UserBase):
    id: int  # User's unique ID

    class Config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy
