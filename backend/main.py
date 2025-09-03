from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from typing import List
import json
import csv
import io
import signal
import sys
import asyncio
from datetime import datetime

from models import QuestionRequest, Question, ValidationResponse, QuestionValidationRequest, HealthResponse
from gemini_generator import question_generator
from validator import validate_multiple_questions
from database import save_question, get_recent_questions
from exporters import export_to_json, export_to_csv, export_to_moodle_xml, export_to_gift, get_timestamp_filename

app = FastAPI(
    title="Smart Quiz Generator API",
    description="API for generating educational quiz questions using AI",
    version="1.0.0"
)

# Global shutdown flag
shutdown_event = asyncio.Event()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Smart Quiz Generator API...")
    print("🤖 Pre-loading AI model...")
    
    # Pre-load model to ensure it's ready
    if question_generator.is_model_loaded():
        print("✅ AI model loaded successfully!")
    else:
        print("⚠️  AI model failed to load - will use fallback mode")
    
    print("📊 Database initialized")
    print("🌐 API server ready!")

@app.on_event("shutdown")
async def shutdown_event_handler():
    """Graceful shutdown handling"""
    print("🔄 Shutting down Smart Quiz Generator API...")
    shutdown_event.set()
    print("✅ Shutdown complete!")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate-questions")
async def generate_questions(request: QuestionRequest):
    """Generate questions from input text"""
    try:
        if not question_generator.is_model_loaded():
            raise HTTPException(status_code=503, detail="ML model not loaded")
        
        if len(request.text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Text too short. Minimum 50 characters required.")
        
        if request.num_questions < 1 or request.num_questions > 20:
            raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 20")
        
        # Generate questions
        questions = question_generator.generate_mcq(request.text, request.num_questions, request.difficulty)
        
        # Save questions to database
        for question in questions:
            try:
                save_question(question)
            except Exception as e:
                print(f"Error saving question: {e}")
        
        return {
            "questions": questions,
            "total_generated": len(questions),
            "request_params": {
                "num_questions": request.num_questions,
                "question_type": request.question_type,
                "difficulty": request.difficulty
            }
        }
    
    except Exception as e:
        print(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@app.post("/api/validate-questions")
async def validate_questions(request: QuestionValidationRequest):
    """Validate questions and return quality scores"""
    try:
        questions_data = [q.dict() for q in request.questions]
        validation_results = validate_multiple_questions(questions_data)
        
        overall_score = sum(result["score"] for result in validation_results) / len(validation_results)
        
        return {
            "overall_score": round(overall_score, 2),
            "individual_results": validation_results,
            "total_questions": len(validation_results),
            "avg_score": round(overall_score, 2)
        }
    
    except Exception as e:
        print(f"Error validating questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating questions: {str(e)}")

@app.get("/api/export/{format}")
async def export_questions(format: str, limit: int = 15):
    """Export questions in specified format (json, csv, moodle, gift)"""
    try:
        questions = get_recent_questions(limit)
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found to export")
        
        if format.lower() == "json":
            content = export_to_json(questions)
            filename = get_timestamp_filename("quiz_export", ".json")
            return Response(
                content=content, 
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif format.lower() == "csv":
            content = export_to_csv(questions)
            filename = get_timestamp_filename("quiz_export", ".csv")
            return Response(
                content=content, 
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif format.lower() == "moodle":
            content = export_to_moodle_xml(questions)
            filename = get_timestamp_filename("quiz_export", ".xml")
            return Response(
                content=content, 
                media_type="application/xml",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif format.lower() == "gift":
            content = export_to_gift(questions)
            filename = get_timestamp_filename("quiz_export", ".gift")
            return Response(
                content=content, 
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use: json, csv, moodle, or gift")
    
    except Exception as e:
        print(f"Error exporting questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting questions: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        model_loaded = question_generator.is_model_loaded()
        return HealthResponse(
            status="running",
            model_loaded=model_loaded
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            model_loaded=False
        )

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🔄 Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting Smart Quiz Generator Backend...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=False,  # Disable reload for production
        access_log=True
    )
