from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionRequest(BaseModel):
    text: str
    num_questions: int
    question_type: str
    difficulty: str

class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str
    bloom_level: str

class ValidationResponse(BaseModel):
    score: int
    feedback: str
    quality_metrics: dict

class QuestionValidationRequest(BaseModel):
    questions: List[Question]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
