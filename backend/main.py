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
async def get_jobs(skip: int = 0, limit: int = 100):
    """Get all active jobs"""
    try:
        from .database.crud import job_crud
        db = next(get_database())
        try:
            jobs = job_crud.get_jobs(db, skip=skip, limit=limit)
            return [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "description": job.description,
                    "requirements": job.requirements,
                    "skills": job.skills,
                    "experience_required": job.experience_required,
                    "location": job.location,
                    "salary_range": job.salary_range,
                    "created_at": job.created_at.isoformat()
                }
                for job in jobs
            ]
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get specific job details"""
    try:
        from .database.crud import job_crud
        db = next(get_database())
        try:
            job = job_crud.get_job_by_id(db, job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            return {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "requirements": job.requirements,
                "skills": job.skills,
                "experience_required": job.experience_required,
                "location": job.location,
                "salary_range": job.salary_range,
                "created_at": job.created_at.isoformat(),
                "recruiter": {
                    "id": job.recruiter.id,
                    "name": job.recruiter.name
                } if job.recruiter else None
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs")
async def create_job(
    job_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new job posting (recruiter only)"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if user["role"] not in ["recruiter", "admin"]:
            raise HTTPException(status_code=403, detail="Only recruiters can create jobs")
        
        from .database.crud import job_crud
        import uuid
        
        db = next(get_database())
        try:
            job_data["id"] = str(uuid.uuid4())
            job_data["recruiter_id"] = user["id"]
            
            job = job_crud.create_job(db, job_data)
            return {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "message": "Job created successfully"
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/applications")
async def submit_application(
    application_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Submit job application"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if user["role"] != "candidate":
            raise HTTPException(status_code=403, detail="Only candidates can submit applications")
        
        from .database.crud import application_crud, job_crud
        import uuid
        
        db = next(get_database())
        try:
            # Verify job exists
            job = job_crud.get_job_by_id(db, application_data["job_id"])
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            # Check if user already applied
            existing_applications = application_crud.get_applications_by_candidate(db, user["id"])
            for app in existing_applications:
                if app.job_id == application_data["job_id"]:
                    raise HTTPException(status_code=400, detail="You have already applied to this job")
            
            # Create application
            application_data["id"] = str(uuid.uuid4())
            application_data["candidate_id"] = user["id"]
            
            application = application_crud.create_application(db, application_data)
            
            return {
                "id": application.id,
                "job_title": job.title,
                "status": application.status,
                "message": "Application submitted successfully"
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/applications/candidate/{candidate_id}")
async def get_candidate_applications(
    candidate_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all applications for a candidate"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if user["id"] != candidate_id and user["role"] not in ["recruiter", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        from .database.crud import application_crud
        db = next(get_database())
        try:
            applications = application_crud.get_applications_by_candidate(db, candidate_id)
            return [
                {
                    "id": app.id,
                    "job": {
                        "id": app.job.id,
                        "title": app.job.title,
                        "company": app.job.company
                    },
                    "status": app.status,
                    "overall_score": app.overall_score,
                    "created_at": app.created_at.isoformat()
                }
                for app in applications
            ]
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/applications/job/{job_id}")
async def get_job_applications(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all applications for a job (recruiter only)"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if user["role"] not in ["recruiter", "admin"]:
            raise HTTPException(status_code=403, detail="Only recruiters can view job applications")
        
        from .database.crud import application_crud, job_crud
        db = next(get_database())
        try:
            # Verify job exists and user has access
            job = job_crud.get_job_by_id(db, job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            if user["role"] == "recruiter" and job.recruiter_id != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            
            applications = application_crud.get_applications_by_job(db, job_id)
            return [
                {
                    "id": app.id,
                    "candidate": {
                        "id": app.candidate.id,
                        "name": app.candidate.name,
                        "email": app.candidate.email
                    },
                    "status": app.status,
                    "overall_score": app.overall_score,
                    "cv_analysis": app.cv_analysis,
                    "created_at": app.created_at.isoformat()
                }
                for app in applications
            ]
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
