from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import event
from datetime import datetime
from .database import Base

# List of valid regions for the user
VALID_REGIONS = ["EU", "US", "ASIA", "AFRICA", "OCEANIA"]

# User model representing the 'users' table in the database
class User(Base):
    __tablename__ = "users"

    # Defining columns for the user table
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    region = Column(String, nullable=False)
    ping = Column(Integer, nullable=False)
    last_login = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, **kwargs):
        # Validate ping value to be between 0 and 1000
        if "ping" in kwargs:
            ping_value = kwargs.get("ping")
            if not (0 <= ping_value <= 1000):
                raise ValueError("Ping must be between 0 and 1000")

        # Validate region value to be one of the allowed regions
        if "region" in kwargs:
            region_value = kwargs.get("region")
            if region_value not in VALID_REGIONS:
                raise ValueError(f"Region must be one of: {', '.join(VALID_REGIONS)}")

        super().__init__(**kwargs)

    # Method to determine the color based on ping value
    def get_ping_color(self):
        if self.ping <= 70:
            return "green"
        elif 70 < self.ping <= 150:
            return "yellow"
        else:
            return "red"

# Auto-update 'updated_at' field when a user record is updated
@event.listens_for(User, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()

