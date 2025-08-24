from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import uvicorn

# Import our modules
from .services.ai_service import AIService
from .services.auth_service import AuthService
from .models.schemas import (
    User, Job, Application, InterviewQuestion, 
    LoginRequest, RegisterRequest, JobApplication,
    CVAnalysis, InterviewResponse
)
from .database.connection import get_database

app = FastAPI(
    title="AI Candidate Screening API",
    description="FastAPI backend with Anthropic Claude integration for intelligent candidate screening",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
ai_service = AIService()
auth_service = AuthService()

@app.get("/")
async def root():
    return {"message": "AI Candidate Screening API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ai": await ai_service.health_check(),
            "database": "connected"
        }
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(request: LoginRequest):
    try:
        result = await auth_service.authenticate_user(request.email, request.password)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/register")
async def register(request: RegisterRequest):
    try:
        result = await auth_service.create_user(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"message": "Logged out successfully"}

# AI-powered endpoints
@app.post("/ai/analyze-cv")
async def analyze_cv(
    cv_text: str,
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        analysis = await ai_service.analyze_cv(cv_text, job_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate-questions")
async def generate_interview_questions(
    job_id: str,
    cv_analysis: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        questions = await ai_service.generate_interview_questions(job_id, cv_analysis)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/evaluate-response")
async def evaluate_interview_response(
    question_id: str,
    response: str,
    context: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        evaluation = await ai_service.evaluate_response(question_id, response, context)
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate-report")
async def generate_candidate_report(
    application_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        report = await ai_service.generate_comprehensive_report(application_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Job management endpoints
@app.get("/jobs")
async def get_jobs():
    # Return available jobs
    pass

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    # Return specific job details
    pass

@app.post("/applications")
async def submit_application(
    application: JobApplication,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Submit job application
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
