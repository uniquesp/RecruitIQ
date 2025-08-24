from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from . import models
from ..models.schemas import RegisterRequest
import bcrypt
from datetime import datetime

class UserCRUD:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, user_data: RegisterRequest, hashed_password: str) -> models.User:
        db_user = models.User(
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: str, update_data: Dict[str, Any]) -> Optional[models.User]:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user

class JobCRUD:
    @staticmethod
    def get_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[models.Job]:
        return db.query(models.Job).filter(models.Job.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_job_by_id(db: Session, job_id: str) -> Optional[models.Job]:
        return db.query(models.Job).filter(
            and_(models.Job.id == job_id, models.Job.is_active == True)
        ).first()
    
    @staticmethod
    def create_job(db: Session, job_data: Dict[str, Any]) -> models.Job:
        db_job = models.Job(**job_data)
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    
    @staticmethod
    def update_job(db: Session, job_id: str, update_data: Dict[str, Any]) -> Optional[models.Job]:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if job:
            for key, value in update_data.items():
                setattr(job, key, value)
            job.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(job)
        return job

class ApplicationCRUD:
    @staticmethod
    def create_application(db: Session, application_data: Dict[str, Any]) -> models.Application:
        db_application = models.Application(**application_data)
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application
    
    @staticmethod
    def get_application_by_id(db: Session, application_id: str) -> Optional[models.Application]:
        return db.query(models.Application).filter(models.Application.id == application_id).first()
    
    @staticmethod
    def get_applications_by_candidate(db: Session, candidate_id: str) -> List[models.Application]:
        return db.query(models.Application).filter(models.Application.candidate_id == candidate_id).all()
    
    @staticmethod
    def get_applications_by_job(db: Session, job_id: str) -> List[models.Application]:
        return db.query(models.Application).filter(models.Application.job_id == job_id).all()
    
    @staticmethod
    def update_application(db: Session, application_id: str, update_data: Dict[str, Any]) -> Optional[models.Application]:
        application = db.query(models.Application).filter(models.Application.id == application_id).first()
        if application:
            for key, value in update_data.items():
                setattr(application, key, value)
            application.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(application)
        return application

class InterviewCRUD:
    @staticmethod
    def create_interview_session(db: Session, session_data: Dict[str, Any]) -> models.InterviewSession:
        db_session = models.InterviewSession(**session_data)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    
    @staticmethod
    def get_interview_session(db: Session, session_id: str) -> Optional[models.InterviewSession]:
        return db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
    
    @staticmethod
    def create_interview_response(db: Session, response_data: Dict[str, Any]) -> models.InterviewResponse:
        db_response = models.InterviewResponse(**response_data)
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response
    
    @staticmethod
    def get_interview_responses(db: Session, session_id: str) -> List[models.InterviewResponse]:
        return db.query(models.InterviewResponse).filter(models.InterviewResponse.session_id == session_id).all()

class ReportCRUD:
    @staticmethod
    def create_candidate_report(db: Session, report_data: Dict[str, Any]) -> models.CandidateReport:
        db_report = models.CandidateReport(**report_data)
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report
    
    @staticmethod
    def get_report_by_application(db: Session, application_id: str) -> Optional[models.CandidateReport]:
        return db.query(models.CandidateReport).filter(
            models.CandidateReport.application_id == application_id
        ).first()

# Export CRUD instances
user_crud = UserCRUD()
job_crud = JobCRUD()
application_crud = ApplicationCRUD()
interview_crud = InterviewCRUD()
report_crud = ReportCRUD()
