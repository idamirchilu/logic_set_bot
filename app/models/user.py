from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)  # Added index
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    last_interaction = Column(DateTime, default=func.now())