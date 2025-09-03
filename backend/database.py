from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

Base = declarative_base()

class QuestionDB(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)
    correct_answer = Column(String(500), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = "sqlite:///./quiz_generator.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_question(question_data):
    """Save question to database"""
    db = SessionLocal()
    try:
        db_question = QuestionDB(
            text=question_data["question"],
            options_json=json.dumps(question_data["options"]),
            correct_answer=question_data["correct_answer"],
            explanation=question_data.get("explanation", ""),
            difficulty=question_data.get("difficulty", "medium")
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_recent_questions(limit=50):
    """Get recent questions from database"""
    db = SessionLocal()
    try:
        questions = db.query(QuestionDB).order_by(QuestionDB.created_at.desc()).limit(limit).all()
        result = []
        for q in questions:
            result.append({
                "id": q.id,
                "question": q.text,
                "options": json.loads(q.options_json),
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "difficulty": q.difficulty,
                "created_at": q.created_at
            })
        return result
    finally:
        db.close()

# Initialize database on module import
init_db()
