-- Akura AI - Student Tracking Migration
-- Run this in Supabase SQL Editor

-- =============================================================================
-- OPTION A: If table exists - just add new columns
-- =============================================================================

ALTER TABLE correction_sessions ADD COLUMN IF NOT EXISTS student_id VARCHAR(255);
ALTER TABLE correction_sessions ADD COLUMN IF NOT EXISTS student_name VARCHAR(255);
ALTER TABLE correction_sessions ADD COLUMN IF NOT EXISTS student_grade VARCHAR(50);

-- Create index for efficient student queries
CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON correction_sessions(student_id);

-- =============================================================================
-- OPTION B: If table doesn't exist - create fresh
-- =============================================================================

-- Table: correction_sessions
CREATE TABLE IF NOT EXISTS correction_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_text TEXT NOT NULL,
    final_text TEXT,
    model_used VARCHAR(255),
    is_demo_mode VARCHAR(10) DEFAULT 'false',
    
    -- Student tracking fields
    student_id VARCHAR(255),
    student_name VARCHAR(255),
    student_grade VARCHAR(50),
    
    -- Statistics
    total_errors INT DEFAULT 0,
    accepted_count INT DEFAULT 0,
    rejected_count INT DEFAULT 0,
    edited_count INT DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Table: correction_actions
CREATE TABLE IF NOT EXISTS correction_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES correction_sessions(id) ON DELETE CASCADE,
    original_word VARCHAR(255) NOT NULL,
    suggestion VARCHAR(255),
    final_word VARCHAR(255),
    action VARCHAR(20),
    pattern VARCHAR(100),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON correction_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON correction_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_actions_session_id ON correction_actions(session_id);

-- =============================================================================
-- VERIFY CHANGES
-- =============================================================================

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'correction_sessions';

