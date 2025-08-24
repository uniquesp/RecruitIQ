-- Updated to use the new table creation script first
-- Initialize PostgreSQL database for AI Candidate Screening
-- Run this script to create the database and initial data

-- First create all tables
\i scripts/create_tables.sql

-- Insert sample users (password is 'password123' for all)
INSERT INTO users (id, email, name, hashed_password, role, created_at, updated_at) VALUES
('user_1', 'admin@company.com', 'Admin User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'admin', NOW(), NOW()),
('user_2', 'recruiter@company.com', 'Sarah Recruiter', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'recruiter', NOW(), NOW()),
('user_3', 'candidate@email.com', 'John Candidate', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'candidate', NOW(), NOW()),
('user_4', 'jane.smith@email.com', 'Jane Smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'candidate', NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- Insert sample jobs
INSERT INTO jobs (id, title, company, description, requirements, skills, experience_required, location, salary_range, recruiter_id, created_at, updated_at) VALUES
('job_1', 'Senior Frontend Developer', 'TechCorp Inc.', 'We are looking for a Senior Frontend Developer to join our dynamic team. You will be responsible for building modern, responsive web applications using React and TypeScript.', 
 '["5+ years of React experience", "Strong TypeScript skills", "Experience with Next.js", "Knowledge of state management", "Testing experience"]'::jsonb,
 '["React", "TypeScript", "Next.js", "CSS", "JavaScript", "Jest", "Redux"]'::jsonb,
 '5+ years', 'Remote', '$120,000 - $150,000', 'user_2', NOW(), NOW()),

('job_2', 'Full Stack Engineer', 'StartupXYZ', 'Join our fast-growing startup as a Full Stack Engineer. You will work on both frontend and backend systems, helping us scale our platform.',
 '["3+ years of full-stack development", "Node.js and React experience", "Database design skills", "API development experience", "Cloud deployment knowledge"]'::jsonb,
 '["React", "Node.js", "PostgreSQL", "REST APIs", "Docker", "AWS", "TypeScript"]'::jsonb,
 '3+ years', 'San Francisco, CA', '$100,000 - $130,000', 'user_2', NOW(), NOW()),

('job_3', 'Python Data Engineer', 'DataCorp', 'We need a skilled Python Data Engineer to build and maintain our data pipelines and analytics infrastructure.',
 '["4+ years Python experience", "ETL pipeline experience", "SQL expertise", "Big data technologies", "Cloud platforms"]'::jsonb,
 '["Python", "SQL", "Apache Spark", "Airflow", "AWS", "Docker", "Pandas"]'::jsonb,
 '4+ years', 'New York, NY', '$110,000 - $140,000', 'user_2', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample applications
INSERT INTO applications (id, candidate_id, job_id, cv_text, cover_letter, status, overall_score) VALUES
('app_1', 'user_3', 'job_1', 
 'John Candidate - Senior Software Engineer with 6 years of experience in full stack development. Expert in React, TypeScript, and Node.js. Led frontend teams at two previous companies. Built scalable web applications serving millions of users.',
 'I am excited to apply for the Senior Frontend Developer position. My extensive React and TypeScript experience makes me a perfect fit for this role.',
 'submitted', 8.5),

('app_2', 'user_4', 'job_2',
 'Jane Smith - Full Stack Developer with 4 years of experience. Proficient in React, Node.js, and PostgreSQL. Experience with AWS deployment and Docker containerization. Built REST APIs and responsive frontends.',
 'I would love to contribute to your startup as a Full Stack Engineer. My experience with your tech stack and startup environment makes me an ideal candidate.',
 'screening', 7.8)
ON CONFLICT (id) DO NOTHING;

-- The rest of the data (interview sessions, responses, reports) will be created through the API
