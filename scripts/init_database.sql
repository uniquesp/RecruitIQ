-- Initialize PostgreSQL database for AI Candidate Screening
-- Run this script to create the database and initial data

-- Create database (run this as postgres superuser)
-- CREATE DATABASE candidate_screening;

-- Connect to the database and create tables
-- The SQLAlchemy models will create the tables automatically
-- This script provides some initial seed data

-- Insert sample users
INSERT INTO users (id, email, name, hashed_password, role, created_at, updated_at) VALUES
('user_1', 'admin@company.com', 'Admin User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'admin', NOW(), NOW()),
('user_2', 'recruiter@company.com', 'Sarah Recruiter', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'recruiter', NOW(), NOW()),
('user_3', 'candidate@email.com', 'John Candidate', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'candidate', NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- Note: The hashed password above is for 'password123'

-- Insert sample jobs
INSERT INTO jobs (id, title, company, description, requirements, skills, experience_required, location, salary_range, recruiter_id, created_at, updated_at) VALUES
('job_1', 'Senior Frontend Developer', 'TechCorp Inc.', 'We are looking for a Senior Frontend Developer to join our dynamic team...', 
 '["5+ years of React experience", "Strong TypeScript skills", "Experience with Next.js", "Knowledge of state management"]',
 '["React", "TypeScript", "Next.js", "CSS", "JavaScript"]',
 '5+ years', 'Remote', '$120,000 - $150,000', 'user_2', NOW(), NOW()),
('job_2', 'Full Stack Engineer', 'StartupXYZ', 'Join our fast-growing startup as a Full Stack Engineer...',
 '["3+ years of full-stack development", "Node.js and React experience", "Database design skills", "API development experience"]',
 '["React", "Node.js", "PostgreSQL", "REST APIs", "Docker"]',
 '3+ years', 'San Francisco, CA', '$100,000 - $130,000', 'user_2', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- The application data will be created through the API as users interact with the system
