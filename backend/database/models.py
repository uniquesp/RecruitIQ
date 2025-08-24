from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # candidate, recruiter, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="candidate")
    jobs_created = relationship("Job", back_populates="recruiter")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON)  # List of requirements
    skills = Column(JSON)  # List of required skills
    experience_required = Column(String)
    location = Column(String)
    salary_range = Column(String)
    recruiter_id = Column(String, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recruiter = relationship("User", back_populates="jobs_created")
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    candidate_id = Column(String, ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("jobs.id"))
    cv_text = Column(Text, nullable=False)
    cover_letter = Column(Text)
    status = Column(String, default="submitted")  # submitted, screening, interview, rejected, hired
    cv_analysis = Column(JSON)  # Store AI analysis results
    overall_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    interview_sessions = relationship("InterviewSession", back_populates="application")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id"))
    status = Column(String, default="pending")  # pending, in_progress, completed
    questions_generated = Column(JSON)  # Store generated questions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="interview_sessions")
    responses = relationship("InterviewResponse", back_populates="session")

class InterviewResponse(Base):
    __tablename__ = "interview_responses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("interview_sessions.id"))
    question_id = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    ai_evaluation = Column(JSON)  # Store AI evaluation results
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="responses")

class CandidateReport(Base):
    __tablename__ = "candidate_reports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id"))
    overall_recommendation = Column(String)  # strong_hire, hire, maybe, no_hire
    overall_score = Column(Float)
    summary = Column(Text)
    strengths = Column(JSON)
    concerns = Column(JSON)
    skill_assessment = Column(JSON)
    interview_performance = Column(JSON)
    next_steps = Column(JSON)
    salary_recommendation = Column(String)
    confidence_level = Column(Float)
    generated_at = Column(DateTime, default=datetime.utcnow)
