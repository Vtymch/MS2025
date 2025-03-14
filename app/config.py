from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

class Settings:
    # Database URL with a default value if not set in the environment
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")
    # Secret key for signing JWT tokens, with a default value if not set in the environment
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM = "HS256"  # JWT signing algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes

# Create a settings instance with the loaded environment variables
settings = Settings()
