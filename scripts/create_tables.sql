-- Create all tables for AI Candidate Screening System
-- This script creates the complete database schema for Neon PostgreSQL

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('candidate', 'recruiter', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    company VARCHAR NOT NULL,
    description TEXT NOT NULL,
    requirements JSONB,
    skills JSONB,
    experience_required VARCHAR,
    location VARCHAR,
    salary_range VARCHAR,
    recruiter_id VARCHAR REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create applications table
CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR PRIMARY KEY,
    candidate_id VARCHAR REFERENCES users(id),
    job_id VARCHAR REFERENCES jobs(id),
    cv_text TEXT NOT NULL,
    cover_letter TEXT,
    status VARCHAR DEFAULT 'submitted' CHECK (status IN ('submitted', 'screening', 'interview', 'rejected', 'hired')),
    cv_analysis JSONB,
    overall_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create interview_sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
    id VARCHAR PRIMARY KEY,
    application_id VARCHAR REFERENCES applications(id),
    status VARCHAR DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
    questions_generated JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create interview_responses table
CREATE TABLE IF NOT EXISTS interview_responses (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR REFERENCES interview_sessions(id),
    question_id VARCHAR NOT NULL,
    question_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    ai_evaluation JSONB,
    score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create candidate_reports table
CREATE TABLE IF NOT EXISTS candidate_reports (
    id VARCHAR PRIMARY KEY,
    application_id VARCHAR REFERENCES applications(id),
    overall_recommendation VARCHAR CHECK (overall_recommendation IN ('strong_hire', 'hire', 'maybe', 'no_hire')),
    overall_score FLOAT,
    summary TEXT,
    strengths JSONB,
    concerns JSONB,
    skill_assessment JSONB,
    interview_performance JSONB,
    next_steps JSONB,
    salary_recommendation VARCHAR,
    confidence_level FLOAT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_jobs_recruiter_id ON jobs(recruiter_id);
CREATE INDEX IF NOT EXISTS idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_application_id ON interview_sessions(application_id);
CREATE INDEX IF NOT EXISTS idx_interview_responses_session_id ON interview_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_candidate_reports_application_id ON candidate_reports(application_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_interview_sessions_updated_at BEFORE UPDATE ON interview_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
