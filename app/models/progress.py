from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    score = Column(Integer, default=0)
    level = Column(Integer, default=1)
    logic_correct = Column(Integer, default=0)
    set_theory_correct = Column(Integer, default=0)
    total_exercises = Column(Integer, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Add relationship
    user = relationship("User", backref="progress")

class CachedResponse(Base):
    __tablename__ = "cached_responses"
    
    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), unique=True, nullable=False)
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())