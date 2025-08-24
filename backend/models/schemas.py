from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: UserRole
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole

class Job(BaseModel):
    id: str
    title: str
    description: str
    required_skills: List[str]
    experience_required: str
    salary_range: Optional[str] = None
    location: str
    created_at: datetime
    created_by: str

class Application(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    cv_text: str
    status: str
    created_at: datetime
    updated_at: datetime

class JobApplication(BaseModel):
    job_id: str
    cv_text: str
    cover_letter: Optional[str] = None

class InterviewQuestion(BaseModel):
    id: str
    question: str
    type: str
    difficulty: str
    focus_area: str
    expected_answer_points: List[str]
    evaluation_criteria: List[str]

class InterviewResponse(BaseModel):
    question_id: str
    response: str
    application_id: str

class CVAnalysis(BaseModel):
    overall_match_score: int
    skills_analysis: Dict[str, Any]
    experience_analysis: Dict[str, Any]
    education_analysis: Dict[str, Any]
    strengths: List[str]
    concerns: List[str]
    recommendation: str
    summary: str
