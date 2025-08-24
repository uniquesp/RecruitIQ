-- Sample data for AI Candidate Screening System

-- Insert sample users
INSERT INTO users (id, email, name, hashed_password, role) VALUES
('admin-001', 'admin@company.com', 'System Admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/SJx/6k7pu', 'admin'),
('recruiter-001', 'recruiter@company.com', 'Jane Smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/SJx/6k7pu', 'recruiter'),
('candidate-001', 'john.doe@email.com', 'John Doe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/SJx/6k7pu', 'candidate'),
('candidate-002', 'sarah.wilson@email.com', 'Sarah Wilson', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/SJx/6k7pu', 'candidate')
ON CONFLICT (email) DO NOTHING;

-- Insert sample jobs
INSERT INTO jobs (id, title, company, description, requirements, skills, experience_required, location, salary_range, recruiter_id) VALUES
('job-001', 'Senior Full Stack Developer', 'TechCorp Inc', 'We are looking for an experienced full stack developer to join our growing team. You will be responsible for developing and maintaining web applications using modern technologies.', 
 '["Bachelor''s degree in Computer Science", "5+ years of experience", "Strong problem-solving skills"]'::jsonb,
 '["JavaScript", "React", "Node.js", "Python", "PostgreSQL", "AWS"]'::jsonb,
 '5+ years', 'San Francisco, CA', '$120,000 - $160,000', 'recruiter-001'),

('job-002', 'Frontend Developer', 'StartupXYZ', 'Join our dynamic startup as a frontend developer. You will work on creating beautiful and responsive user interfaces for our web applications.',
 '["3+ years frontend experience", "Portfolio of projects", "Team collaboration skills"]'::jsonb,
 '["React", "TypeScript", "CSS", "HTML", "Git", "Figma"]'::jsonb,
 '3+ years', 'Remote', '$80,000 - $110,000', 'recruiter-001'),

('job-003', 'Data Scientist', 'DataTech Solutions', 'We are seeking a data scientist to help us extract insights from large datasets and build predictive models.',
 '["Master''s in Data Science or related field", "Experience with ML frameworks", "Statistical analysis skills"]'::jsonb,
 '["Python", "R", "TensorFlow", "SQL", "Statistics", "Machine Learning"]'::jsonb,
 '4+ years', 'New York, NY', '$100,000 - $140,000', 'recruiter-001')
ON CONFLICT (id) DO NOTHING;

-- Insert sample applications
INSERT INTO applications (id, candidate_id, job_id, cv_text, cover_letter, status, overall_score) VALUES
('app-001', 'candidate-001', 'job-001', 
 'John Doe - Senior Software Engineer with 6 years of experience in full stack development. Proficient in JavaScript, React, Node.js, Python, and PostgreSQL. Led multiple projects at previous companies.',
 'I am excited to apply for the Senior Full Stack Developer position. My experience aligns perfectly with your requirements.',
 'submitted', 8.5),

('app-002', 'candidate-002', 'job-002',
 'Sarah Wilson - Frontend Developer with 4 years of experience. Expert in React, TypeScript, and modern CSS. Created responsive web applications for various clients.',
 'I would love to contribute to your startup''s frontend development. My portfolio showcases my skills in creating engaging user interfaces.',
 'screening', 7.8)
ON CONFLICT (id) DO NOTHING;
