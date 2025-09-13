from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50))
    created_at = Column(DateTime, default=func.now())