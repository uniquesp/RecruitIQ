import anthropic
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from ..database.crud import job_crud, application_crud, interview_crud, report_crud
from ..database.connection import get_database

class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-3-5-sonnet-20241022"
    
    async def health_check(self) -> str:
        """Check if AI service is working"""
        try:
            # Simple test call to verify API key and connection
            response = await self._make_ai_request(
                "Respond with 'OK' if you can read this message.",
                max_tokens=10
            )
            return "healthy" if "OK" in response else "degraded"
        except Exception:
            return "unhealthy"
    
    async def _make_ai_request(self, prompt: str, max_tokens: int = 1000, system_prompt: str = None) -> str:
        """Make a request to Claude API"""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = self.client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            raise Exception(f"AI service error: {str(e)}")
    
    async def analyze_cv(self, cv_text: str, job_id: str) -> Dict[str, Any]:
        """Analyze CV against job requirements using Claude"""
        
        # Get job details from database
        db = next(get_database())
        try:
            job = job_crud.get_job_by_id(db, job_id)
            if not job:
                raise Exception("Job not found")
            
            job_details = {
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "skills": job.skills,
                "experience_required": job.experience_required
            }
        finally:
            db.close()
        
        system_prompt = """You are an expert HR analyst. Analyze the provided CV against the job requirements and return a structured JSON response with the following format:
        {
            "overall_match_score": 0-100,
            "skills_analysis": {
                "matched_skills": ["skill1", "skill2"],
                "missing_skills": ["skill3", "skill4"],
                "skill_match_percentage": 0-100
            },
            "experience_analysis": {
                "relevant_experience_years": number,
                "experience_match_score": 0-100,
                "key_experiences": ["exp1", "exp2"]
            },
            "education_analysis": {
                "education_match_score": 0-100,
                "relevant_qualifications": ["qual1", "qual2"]
            },
            "strengths": ["strength1", "strength2"],
            "concerns": ["concern1", "concern2"],
            "recommendation": "hire|interview|reject",
            "summary": "Brief summary of the analysis"
        }"""
        
        prompt = f"""
        Job Requirements:
        {json.dumps(job_details, indent=2)}
        
        Candidate CV:
        {cv_text}
        
        Please analyze this CV against the job requirements and provide a detailed assessment.
        """
        
        response = await self._make_ai_request(prompt, max_tokens=2000, system_prompt=system_prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "overall_match_score": 50,
                "summary": response,
                "error": "Failed to parse structured response"
            }
    
    async def generate_interview_questions(self, job_id: str, cv_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized interview questions based on CV analysis"""
        
        # Get job details from database
        db = next(get_database())
        try:
            job = job_crud.get_job_by_id(db, job_id)
            if not job:
                raise Exception("Job not found")
            
            job_details = {
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "skills": job.skills
            }
        finally:
            db.close()
        
        system_prompt = """You are an expert interviewer. Generate 5-7 personalized interview questions based on the job requirements and CV analysis. Return a JSON array with this format:
        [
            {
                "id": "unique_id",
                "question": "The interview question",
                "type": "technical|behavioral|situational",
                "difficulty": "easy|medium|hard",
                "focus_area": "skills|experience|culture_fit",
                "expected_answer_points": ["point1", "point2"],
                "evaluation_criteria": ["criteria1", "criteria2"]
            }
        ]"""
        
        prompt = f"""
        Job Details:
        {json.dumps(job_details, indent=2)}
        
        CV Analysis:
        {json.dumps(cv_analysis, indent=2)}
        
        Generate personalized interview questions that:
        1. Test the candidate's claimed skills
        2. Explore areas where they might be weak
        3. Assess cultural fit
        4. Validate their experience claims
        """
        
        response = await self._make_ai_request(prompt, max_tokens=2000, system_prompt=system_prompt)
        
        try:
            questions = json.loads(response)
            # Add timestamps and IDs
            for i, q in enumerate(questions):
                q["id"] = f"q_{job_id}_{i}_{int(datetime.now().timestamp())}"
                q["created_at"] = datetime.now().isoformat()
            return questions
        except json.JSONDecodeError:
            # Fallback questions
            return [
                {
                    "id": f"fallback_{int(datetime.now().timestamp())}",
                    "question": "Tell me about your experience with the technologies mentioned in your CV.",
                    "type": "technical",
                    "difficulty": "medium",
                    "focus_area": "skills"
                }
            ]
    
    async def evaluate_response(self, question_id: str, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate candidate's response to interview question"""
        
        system_prompt = """You are an expert interviewer evaluating a candidate's response. Return a JSON response with this format:
        {
            "score": 0-100,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "follow_up_questions": ["question1", "question2"],
            "overall_assessment": "excellent|good|average|poor",
            "detailed_feedback": "Detailed explanation of the evaluation"
        }"""
        
        prompt = f"""
        Question Context:
        {json.dumps(context, indent=2)}
        
        Candidate Response:
        {response}
        
        Evaluate this response considering:
        1. Technical accuracy (if applicable)
        2. Communication clarity
        3. Depth of knowledge
        4. Problem-solving approach
        5. Relevance to the question
        """
        
        ai_response = await self._make_ai_request(prompt, max_tokens=1500, system_prompt=system_prompt)
        
        try:
            evaluation = json.loads(ai_response)
            evaluation["question_id"] = question_id
            evaluation["evaluated_at"] = datetime.now().isoformat()
            return evaluation
        except json.JSONDecodeError:
            return {
                "score": 50,
                "overall_assessment": "average",
                "detailed_feedback": ai_response,
                "question_id": question_id,
                "evaluated_at": datetime.now().isoformat()
            }
    
    async def generate_comprehensive_report(self, application_id: str) -> Dict[str, Any]:
        """Generate final comprehensive candidate report"""
        
        # Get all application data from database
        db = next(get_database())
        try:
            application = application_crud.get_application_by_id(db, application_id)
            if not application:
                raise Exception("Application not found")
            
            # Get interview responses
            interview_sessions = db.query(models.InterviewSession).filter(
                models.InterviewSession.application_id == application_id
            ).all()
            
            interview_responses = []
            for session in interview_sessions:
                responses = interview_crud.get_interview_responses(db, session.id)
                interview_responses.extend(responses)
            
            application_data = {
                "cv_analysis": application.cv_analysis,
                "interview_responses": [
                    {
                        "question": resp.question_text,
                        "response": resp.response_text,
                        "evaluation": resp.ai_evaluation,
                        "score": resp.score
                    } for resp in interview_responses
                ],
                "job_details": {
                    "title": application.job.title,
                    "requirements": application.job.requirements
                }
            }
        finally:
            db.close()
        
        system_prompt = """You are an expert HR consultant generating a comprehensive candidate evaluation report. Return a JSON response with this format:
        {
            "overall_recommendation": "strong_hire|hire|maybe|no_hire",
            "overall_score": 0-100,
            "summary": "Executive summary of the candidate",
            "strengths": ["strength1", "strength2"],
            "concerns": ["concern1", "concern2"],
            "skill_assessment": {
                "technical_skills": 0-100,
                "communication": 0-100,
                "problem_solving": 0-100,
                "cultural_fit": 0-100
            },
            "interview_performance": {
                "average_score": 0-100,
                "best_responses": ["response1", "response2"],
                "areas_for_improvement": ["area1", "area2"]
            },
            "next_steps": ["step1", "step2"],
            "salary_recommendation": "market_rate|above_market|below_market",
            "confidence_level": 0-100
        }"""
        
        prompt = f"""
        Complete Application Data:
        {json.dumps(application_data, indent=2)}
        
        Generate a comprehensive evaluation report that synthesizes all available information about this candidate.
        """
        
        response = await self._make_ai_request(prompt, max_tokens=3000, system_prompt=system_prompt)
        
        try:
            report = json.loads(response)
            report["generated_at"] = datetime.now().isoformat()
            report["application_id"] = application_id
            
            # Save report to database
            db = next(get_database())
            try:
                report_crud.create_candidate_report(db, report)
            finally:
                db.close()
            
            return report
        except json.JSONDecodeError:
            return {
                "overall_recommendation": "maybe",
                "overall_score": 50,
                "summary": response,
                "generated_at": datetime.now().isoformat(),
                "application_id": application_id
            }
